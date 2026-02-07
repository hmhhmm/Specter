#!/usr/bin/env python3
"""ghost_mode.py - The Ghost Brain (Mystery Shopper).

A standalone agent loop that reuses webqa-agent's browser and LLM
infrastructure to drive an autonomous signup flow via a three-phase
Observe > Insight > Act cycle.

Each step produces a rich JSON report with:
  - before/after screenshots saved to ./logs/
  - network request logs (status, url, method)
  - browser console logs
  - LLM-generated outcome diagnosis (status, severity, responsible team)

Usage:
    python ghost_mode.py [--persona cautious] [--headless]
"""

import argparse
import asyncio
import base64
import json
import logging
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# -- webqa-agent imports (keep the core) ------------------------------
from webqa_agent.browser.session import BrowserSessionPool
from webqa_agent.llm.llm_api import LLMAPI
from webqa_agent.utils.get_log import GetLog

# -- Constants -----------------------------------------------------------------
TARGET_URL = "https://deriv.com/signup"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_STEPS = 25
OBSERVE_DELAY = 2.0
LLM_MAX_RETRIES = 5
LLM_BASE_DELAY = 4.0
LOGS_DIR = Path("./logs")

# -- System prompt (Insight + Action) ------------------------------------------
SYSTEM_PROMPT = """\
You are Ghost Agent, an autonomous browser pilot AND a UX mystery shopper.

You receive a screenshot of a web page. You must do two things:

1. **UX Insight** - Evaluate the current screen from a real user's perspective.
2. **Next Action** - Decide the single best action to progress through a
   signup flow.

Also provide your expectation of what SHOULD happen after the action.

Respond with ONLY valid JSON (no markdown fences, no explanation outside JSON):

{
  "ux_insight": {
    "confusion_score": <int 0-10>,
    "friction": "<short UX friction description or 'none'>"
  },
  "action": "click" | "type" | "scroll" | "done" | "wait",
  "coordinates": [x, y],
  "value": "<text to type if 'type', direction if 'scroll', else empty string>",
  "thought": "<one-sentence reasoning>",
  "expectation": "<what you expect to see after this action, e.g. 'A dropdown menu should appear with country options'>"
}

Scoring guide for confusion_score:
  0 - Perfectly clear, obvious next step
  1-3 - Minor friction (small label issues, extra scrolling needed)
  4-6 - Moderate confusion (ambiguous CTA, unclear form fields)
  7-9 - High confusion (misleading text, broken layout, hidden elements)
  10 - Completely stuck, no idea how to proceed

Rules:
- coordinates are CSS pixels relative to viewport top-left (0,0).
- "done" means the signup task is complete.
- "wait" means nothing actionable yet; the agent will retry.
- For "scroll", coordinates can be [0, 0] and value "up" or "down".
- Always pick the most logical next step toward completing the signup form.
"""

# -- Diagnosis prompt (sent AFTER action with before + after screenshots) ------
DIAGNOSIS_PROMPT = """\
You are a QA engineer diagnosing the outcome of a browser action.

You will receive TWO screenshots:
1. BEFORE the action was taken
2. AFTER the action was taken

The action was: {action_description}
The agent expected: {expectation}

Analyze the visual difference and respond with ONLY valid JSON:

{{
  "status": "PASSED" | "FAILED" | "PARTIAL" | "BLOCKED",
  "visual_observation": "<describe what visually changed or did not change>",
  "diagnosis": "<root cause if failed, e.g. 'Backend API Failure', 'Element not interactable', 'Page did not respond'>",
  "severity": "<one of: 'P0 - Critical Blocker', 'P1 - Major', 'P2 - Minor', 'P3 - Cosmetic', 'P4 - Enhancement'>",
  "responsible_team": "<one of: 'Frontend Engineering', 'Backend Engineering', 'UX/Design', 'QA', 'DevOps', 'Product'>"
}}

If the action succeeded as expected, use status "PASSED", severity "P4 - Enhancement",
responsible_team "N/A", and diagnosis "Action completed as expected".
"""

# -- Red-dot debug overlay JS --------------------------------------------------
RED_DOT_JS = """
(coords) => {
    const old = document.getElementById('__ghost_dot__');
    if (old) old.remove();

    const dot = document.createElement('div');
    dot.id = '__ghost_dot__';
    dot.style.cssText = `
        position: fixed;
        left: ${coords[0] - 8}px;
        top: ${coords[1] - 8}px;
        width: 16px;
        height: 16px;
        background: red;
        border: 2px solid white;
        border-radius: 50%;
        z-index: 2147483647;
        pointer-events: none;
        box-shadow: 0 0 6px 2px rgba(255,0,0,0.6);
        transition: opacity 0.3s;
    `;
    document.body.appendChild(dot);
    setTimeout(() => { dot.style.opacity = '0'; }, 2000);
    setTimeout(() => { dot.remove(); }, 2500);
}
"""


class GhostAgentLoop:
    """Observe > Insight > Act loop with full JSON report per step."""

    def __init__(
        self,
        llm_config: Dict[str, Any],
        browser_config: Optional[Dict[str, Any]] = None,
        persona: str = "default",
        target_url: str = TARGET_URL,
        max_steps: int = MAX_STEPS,
    ):
        self.llm_config = llm_config
        self.browser_config = browser_config or {
            "browser_type": "chromium",
            "viewport": {"width": 1280, "height": 720},
            "device_scale_factor": 1.0,
            "headless": False,
            "language": "en-US",
        }
        self.persona = persona
        self.target_url = target_url
        self.max_steps = max_steps

        self.llm = LLMAPI(llm_config)
        self.pool = BrowserSessionPool(
            pool_size=1,
            browser_config=self.browser_config,
        )

        self._step = 0
        self.ux_insights: List[Dict[str, Any]] = []
        self.step_reports: List[Dict[str, Any]] = []

        # Captured during page lifecycle
        self._network_logs: List[Dict[str, Any]] = []
        self._console_logs: List[str] = []

    # -- Network + console listeners -------------------------------------------

    def _attach_listeners(self, page):
        """Hook into Playwright page events for network and console capture."""

        def on_response(response):
            status = response.status
            # Capture 4xx/5xx and all API-like calls
            if status >= 400 or "/api" in response.url:
                self._network_logs.append({
                    "status": status,
                    "url": response.url,
                    "method": response.request.method,
                })

        def on_console(msg):
            if msg.type in ("error", "warning"):
                self._console_logs.append(f"[{msg.type}] {msg.text}")

        page.on("response", on_response)
        page.on("console", on_console)

    def _flush_logs(self) -> tuple:
        """Return and clear captured network + console logs for this step."""
        net = list(self._network_logs)
        con = list(self._console_logs)
        self._network_logs.clear()
        self._console_logs.clear()
        return net, con

    # -- Screenshot helpers ----------------------------------------------------

    async def _take_screenshot(self, page, step: int, label: str) -> str:
        """Take screenshot, save to logs/, return relative path."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"step_{step:02d}_{label}.png"
        filepath = LOGS_DIR / filename
        png_bytes = await page.screenshot(type="png", full_page=False)
        filepath.write_bytes(png_bytes)
        return f"./logs/{filename}"

    async def _screenshot_b64(self, page) -> str:
        """Take screenshot and return base64 for LLM."""
        png_bytes = await page.screenshot(type="png", full_page=False)
        return base64.b64encode(png_bytes).decode("utf-8")

    # -- Public entry point ----------------------------------------------------
    async def run(self) -> Dict[str, Any]:
        """Execute the full Ghost Agent loop. Returns a summary dict."""
        await self.llm.initialize()
        logging.info("Ghost Agent initialized  |  persona=%s", self.persona)

        session = await self.pool.acquire(timeout=30.0)
        history: List[Dict[str, Any]] = []

        try:
            page = session.page
            self._attach_listeners(page)

            await session.navigate_to(self.target_url)
            logging.info("Navigated to %s", self.target_url)
            await asyncio.sleep(2.0)

            for step in range(1, self.max_steps + 1):
                self._step = step
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

                # -- 1. OBSERVE (before screenshot) ---------------------------
                try:
                    before_path = await self._take_screenshot(page, step, "before")
                    before_b64 = await self._screenshot_b64(page)
                except Exception as ss_err:
                    logging.error("Step %d -- screenshot failed: %s", step, ss_err)
                    break
                logging.info("Step %d -- screenshot captured", step)

                # -- 2. INSIGHT + DECIDE (single LLM call) --------------------
                self._flush_logs()  # clear logs before action
                decision = await self._decide(before_b64)
                if decision is None:
                    logging.warning("Step %d -- LLM returned unparseable response, retrying", step)
                    await asyncio.sleep(1.0)
                    continue

                # Extract UX insight
                ux = decision.get("ux_insight", {})
                confusion = ux.get("confusion_score", -1)
                friction = ux.get("friction", "n/a")
                self.ux_insights.append({"step": step, **ux})
                logging.info(
                    "Step %d -- UX confusion=%d/10  friction='%s'",
                    step, confusion, friction,
                )

                action = decision.get("action", "wait")
                coords = decision.get("coordinates", [0, 0])
                value = decision.get("value", "")
                thought = decision.get("thought", "")
                expectation = decision.get("expectation", "")
                logging.info(
                    "Step %d -- action=%s  coords=%s  thought=%s",
                    step, action, coords, thought,
                )

                if action == "done":
                    # Build final report for "done"
                    report = self._build_report(
                        step, timestamp, action, coords, value,
                        expectation, before_path, before_path,
                        {"status": "PASSED", "visual_observation": "Signup task completed",
                         "diagnosis": "Action completed as expected",
                         "severity": "P4 - Enhancement", "responsible_team": "N/A"},
                        [], [], decision,
                    )
                    self.step_reports.append(report)
                    history.append(report)
                    logging.info("Ghost Agent finished at step %d", step)
                    break

                if action == "wait":
                    await asyncio.sleep(2.0)
                    continue

                # -- 3. ACT ---------------------------------------------------
                action_desc = self._describe_action(action, coords, value)
                await self._act(page, action, coords, value)
                await asyncio.sleep(OBSERVE_DELAY)

                # -- 4. AFTER screenshot + capture logs -----------------------
                try:
                    after_path = await self._take_screenshot(page, step, "after")
                    after_b64 = await self._screenshot_b64(page)
                except Exception:
                    after_path = before_path
                    after_b64 = before_b64

                net_logs, con_logs = self._flush_logs()

                # -- 5. DIAGNOSE outcome (second LLM call) --------------------
                outcome = await self._diagnose(
                    before_b64, after_b64, action_desc, expectation,
                )
                if outcome is None:
                    outcome = {
                        "status": "PARTIAL",
                        "visual_observation": "Diagnosis unavailable",
                        "diagnosis": "LLM diagnosis call failed",
                        "severity": "P2 - Minor",
                        "responsible_team": "QA",
                    }

                # -- 6. BUILD STEP REPORT (your JSON schema) ------------------
                report = self._build_report(
                    step, timestamp, action, coords, value,
                    expectation, before_path, after_path,
                    outcome, net_logs, con_logs, decision,
                )
                self.step_reports.append(report)
                history.append(report)

                # Save individual step JSON
                step_file = LOGS_DIR / f"step_{step:02d}_report.json"
                step_file.write_text(json.dumps(report, indent=2))
                logging.info(
                    "Step %d -- outcome=%s  severity=%s",
                    step, outcome.get("status"), outcome.get("severity"),
                )

            else:
                logging.warning("Max steps (%d) reached without completion", self.max_steps)

        finally:
            await self.pool.release(session)
            await self.pool.close_all()

        # -- Write full run report ---------------------------------------------
        avg_confusion = 0.0
        if self.ux_insights:
            scores = [i.get("confusion_score", 0) for i in self.ux_insights]
            avg_confusion = sum(scores) / len(scores)

        run_report = {
            "run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            "target_url": self.target_url,
            "persona": self.persona,
            "model": self.llm_config.get("model", "unknown"),
            "total_steps": len(self.step_reports),
            "completed": self.step_reports[-1].get("outcome", {}).get("status") == "PASSED"
                         and self.step_reports[-1].get("action_taken", "").startswith("done")
                         if self.step_reports else False,
            "avg_confusion_score": round(avg_confusion, 2),
            "steps": self.step_reports,
        }

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        full_report_path = LOGS_DIR / "ghost_run_report.json"
        full_report_path.write_text(json.dumps(run_report, indent=2))
        logging.info("Full report saved to %s", full_report_path)

        return run_report

    # -- Private helpers -------------------------------------------------------

    def _describe_action(self, action: str, coords: List, value: str) -> str:
        """Human-readable description of the action."""
        x, y = coords[0], coords[1]
        if action == "click":
            return f"Clicked at ({x}, {y})"
        elif action == "type":
            return f"Typed '{value}' at ({x}, {y})"
        elif action == "scroll":
            return f"Scrolled {value or 'down'}"
        return f"{action} at ({x}, {y})"

    def _build_report(
        self,
        step: int,
        timestamp: str,
        action: str,
        coords: List,
        value: str,
        expectation: str,
        before_path: str,
        after_path: str,
        outcome: Dict[str, Any],
        net_logs: List[Dict[str, Any]],
        con_logs: List[str],
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the full JSON report for a single step."""
        return {
            "step_id": step,
            "timestamp": timestamp,
            "persona": self.persona,
            "action_taken": self._describe_action(action, coords, value),
            "agent_expectation": expectation,
            "ux_insight": decision.get("ux_insight", {}),
            "outcome": {
                "status": outcome.get("status", "PARTIAL"),
                "visual_observation": outcome.get("visual_observation", ""),
                "diagnosis": outcome.get("diagnosis", ""),
                "severity": outcome.get("severity", "P2 - Minor"),
                "responsible_team": outcome.get("responsible_team", "QA"),
            },
            "evidence": {
                "screenshot_before_path": before_path,
                "screenshot_after_path": after_path,
                "network_logs": net_logs,
                "console_logs": con_logs,
            },
        }

    async def _decide(self, screenshot_b64: str) -> Optional[Dict[str, Any]]:
        """Send screenshot to LLM with exponential backoff on rate limits."""
        image_data = f"data:image/png;base64,{screenshot_b64}"
        delay = LLM_BASE_DELAY

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                raw = await self.llm.get_llm_response(
                    system_prompt=SYSTEM_PROMPT,
                    prompt=(
                        f"Step {self._step} of {self.max_steps}. "
                        "Evaluate the UX and pick the best next action. JSON only."
                    ),
                    images=[image_data],
                    temperature=0.3,
                    max_tokens=768,
                )
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()

                return json.loads(cleaned)
            except json.JSONDecodeError:
                logging.error(
                    "JSON parse failed (attempt %d). Raw:\n%s",
                    attempt, raw if "raw" in dir() else "<unavailable>",
                )
                return None
            except Exception as exc:
                err_msg = str(exc).lower()
                if "rate limit" in err_msg or "429" in err_msg:
                    if attempt < LLM_MAX_RETRIES:
                        logging.warning(
                            "Rate limited (attempt %d/%d). Waiting %.0fs...",
                            attempt, LLM_MAX_RETRIES, delay,
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, 60.0)
                        continue
                logging.error("LLM call failed: %s", exc)
                return None

        logging.error("All %d LLM retries exhausted.", LLM_MAX_RETRIES)
        return None

    async def _diagnose(
        self,
        before_b64: str,
        after_b64: str,
        action_description: str,
        expectation: str,
    ) -> Optional[Dict[str, Any]]:
        """Second LLM call: compare before/after screenshots to diagnose outcome."""
        before_img = f"data:image/png;base64,{before_b64}"
        after_img = f"data:image/png;base64,{after_b64}"
        prompt_text = DIAGNOSIS_PROMPT.format(
            action_description=action_description,
            expectation=expectation,
        )
        delay = LLM_BASE_DELAY

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                raw = await self.llm.get_llm_response(
                    system_prompt="You are a QA diagnosis engine. Respond with JSON only.",
                    prompt=prompt_text,
                    images=[before_img, after_img],
                    temperature=0.2,
                    max_tokens=512,
                )
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()

                return json.loads(cleaned)
            except json.JSONDecodeError:
                logging.error("Diagnosis JSON parse failed. Raw:\n%s",
                              raw if "raw" in dir() else "<unavailable>")
                return None
            except Exception as exc:
                err_msg = str(exc).lower()
                if "rate limit" in err_msg or "429" in err_msg:
                    if attempt < LLM_MAX_RETRIES:
                        logging.warning(
                            "Diagnosis rate limited (attempt %d/%d). Waiting %.0fs...",
                            attempt, LLM_MAX_RETRIES, delay,
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, 60.0)
                        continue
                logging.error("Diagnosis LLM call failed: %s", exc)
                return None

        return None

    async def _act(
        self,
        page,
        action: str,
        coords: List,
        value: str = "",
    ):
        """Execute a single action on the page with persona behaviour."""
        x, y = float(coords[0]), float(coords[1])

        # -- Persona: cautious -- hesitation delay + scroll ----------------
        if self.persona == "cautious":
            await asyncio.sleep(2.0)
            await page.mouse.wheel(0, 80)
            await asyncio.sleep(0.4)
            await page.mouse.wheel(0, -80)
            await asyncio.sleep(0.3)

        # -- Visual debug: inject red dot ----------------------------------
        try:
            await page.evaluate(RED_DOT_JS, [x, y])
        except Exception:
            pass

        # -- Execute the action --------------------------------------------
        if action == "click":
            logging.info("Click at (%.0f, %.0f)", x, y)
            await page.mouse.click(x, y)

        elif action == "type":
            logging.info("Type '%s' at (%.0f, %.0f)", value, x, y)
            await page.mouse.click(x, y)
            await asyncio.sleep(0.2)
            for char in value:
                await page.keyboard.type(char, delay=random.randint(30, 90))

        elif action == "scroll":
            direction = value.lower() if value else "down"
            delta = -300 if direction == "up" else 300
            logging.info("Scroll %s", direction)
            await page.mouse.wheel(0, delta)

        else:
            logging.warning("Unknown action '%s' - skipping", action)


# -- CLI entry point -----------------------------------------------------------

async def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Ghost Agent - autonomous UX mystery shopper")
    parser.add_argument("--persona", choices=["default", "cautious"], default="default",
                        help="'cautious' adds 2s hesitation delay and scroll before every click")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--url", default=TARGET_URL, help="Target URL to navigate to")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS, help="Maximum agent steps")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    args = parser.parse_args()

    GetLog.get_log(log_level="info")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logging.error("ANTHROPIC_API_KEY is not set. Add it to .env or export it.")
        sys.exit(1)

    llm_config = {
        "api": "anthropic",
        "model": args.model,
        "api_key": api_key,
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    browser_config = {
        "browser_type": "chromium",
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1.0,
        "headless": args.headless,
        "language": "en-US",
    }

    agent = GhostAgentLoop(
        llm_config=llm_config,
        browser_config=browser_config,
        persona=args.persona,
        target_url=args.url,
        max_steps=args.max_steps,
    )

    result = await agent.run()

    # -- Summary ---------------------------------------------------------------
    print("\n" + "=" * 64)
    print("  Ghost Agent Run Report")
    print(f"  Persona            : {result['persona']}")
    print(f"  Model              : {result['model']}")
    print(f"  Steps taken        : {result['total_steps']}")
    print(f"  Completed          : {'Yes' if result['completed'] else 'No'}")
    print(f"  Avg Confusion Score: {result['avg_confusion_score']}/10")
    print("=" * 64)

    print("\n  -- Step Reports --")
    for r in result["steps"]:
        status = r.get("outcome", {}).get("status", "?")
        severity = r.get("outcome", {}).get("severity", "?")
        action = r.get("action_taken", "?")
        obs = r.get("outcome", {}).get("visual_observation", "")[:80]
        print(f"  [{r['step_id']:>2}] {status:<8} {severity:<20} {action}")
        if obs:
            print(f"       -> {obs}")

    net_count = sum(len(r.get("evidence", {}).get("network_logs", [])) for r in result["steps"])
    con_count = sum(len(r.get("evidence", {}).get("console_logs", [])) for r in result["steps"])
    print(f"\n  Network errors captured: {net_count}")
    print(f"  Console errors captured: {con_count}")
    print(f"\n  Full report: ./logs/ghost_run_report.json")


if __name__ == "__main__":
    asyncio.run(main())
