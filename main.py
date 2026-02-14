#!/usr/bin/env python3
"""
SPECTER - Autonomous AI QA Agent
Fully powered by webqa_agent + raw Anthropic API.

  BrowserSessionPool  - managed browser lifecycle
  DeepCrawler          - DOM element detection + highlight
  ActionHandler         - click, type, scroll, hover, screenshots
  ActionExecutor        - structured action dispatch
  ScrollHandler         - smart page/container scrolling
  Raw Anthropic API     - vision + reasoning (claude-sonnet-4-20250514)

FEATURE 1: Multimodal Persona-Driven Navigator
  - LLM observes screenshot + DOM -> decides next action autonomously
  - Persona simulation (zoomer, boomer, skeptic, chaos, mobile)
  - Device emulation, network throttling, locale
  - AI decides ALL steps -- no hardcoded sequences

FEATURE 2: Cognitive UX Analyst & Diagnosis
  - F-Score calculation, Heatmap, GIF replay
  - P0-P3 severity, Claude Vision diagnosis, Slack escalation

Usage:
    python main.py                                    # Demo with mock data
    python main.py autonomous https://example.com    # Full autonomous test
    python main.py autonomous https://deriv.com/signup --persona boomer --device iphone13
"""

import asyncio
import sys
import os
import argparse
import json
import base64
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional

# Specter Core - Feature 2 (Diagnosis Engine)
from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert
from backend.webqa_bridge import _resolve_screenshot_path

# Specter Core - CAPTCHA and OTP Handling
from backend.captcha_handler import CaptchaDetector, CaptchaSolver
from backend.otp_reader import OTPReader

# Raw Anthropic SDK
import anthropic
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))

# webqa_agent - the REAL agent infrastructure
try:
    from webqa_agent.browser.session import BrowserSessionPool
    from webqa_agent.actions.action_handler import ActionHandler
    from webqa_agent.actions.action_executor import ActionExecutor
    from webqa_agent.actions.scroll_handler import ScrollHandler
    from webqa_agent.crawler.deep_crawler import DeepCrawler
    AUTONOMOUS_AVAILABLE = True
except ImportError as e:
    AUTONOMOUS_AVAILABLE = False
    print(f"Autonomous mode requires webqa_agent: {e}")


# ======================================================================
# RED DOT DEBUG OVERLAY
# ======================================================================

RED_DOT_JS = """
(coords) => {
    const old = document.getElementById('__ghost_dot__');
    if (old) old.remove();
    const dot = document.createElement('div');
    dot.id = '__ghost_dot__';
    dot.style.cssText = `
        position: fixed;
        left: ${coords[0] - 20}px;
        top: ${coords[1] - 20}px;
        width: 40px; height: 40px;
        background: radial-gradient(circle, rgba(255,0,0,0.9) 0%, rgba(255,0,0,0.6) 70%);
        border: 4px solid rgba(255,255,255,0.9);
        border-radius: 50%;
        z-index: 2147483647;
        pointer-events: none;
        box-shadow: 0 0 20px 8px rgba(255,0,0,0.8), 0 0 40px 15px rgba(255,100,100,0.5);
        animation: ghostPulse 0.6s ease-out, ghostGlow 1.5s ease-in-out infinite;
    `;
    const style = document.createElement('style');
    style.textContent = '@keyframes ghostPulse { 0% { transform: scale(0.3); opacity: 0; } 50% { transform: scale(1.3); opacity: 1; } 100% { transform: scale(1); opacity: 1; } } @keyframes ghostGlow { 0%, 100% { box-shadow: 0 0 20px 8px rgba(255,0,0,0.8), 0 0 40px 15px rgba(255,100,100,0.5); } 50% { box-shadow: 0 0 30px 12px rgba(255,0,0,1), 0 0 60px 25px rgba(255,100,100,0.8); } }';
    document.head.appendChild(style);
    document.body.appendChild(dot);
    setTimeout(() => { dot.style.opacity = '0'; dot.style.transition = 'opacity 1s ease-out'; }, 4000);
    setTimeout(() => { dot.remove(); style.remove(); }, 5000);
}
"""


# ======================================================================
# DEVICE / NETWORK / PERSONA PROFILES
# ======================================================================

DEVICES = {
    'iphone13': {
        'name': 'iPhone 13 Pro',
        'viewport': {'width': 390, 'height': 844},
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
        'has_touch': True, 'is_mobile': True,
    },
    'android': {
        'name': 'Pixel 5',
        'viewport': {'width': 393, 'height': 851},
        'user_agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36',
        'has_touch': True, 'is_mobile': True,
    },
    'desktop': {
        'name': 'Desktop 1280x720',
        'viewport': {'width': 1280, 'height': 720},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'has_touch': False, 'is_mobile': False,
    },
}

NETWORKS = {
    '3g':   {'name': 'Slow 3G',  'download': 400*1024//8,     'upload': 400*1024//8,     'latency': 400},
    '4g':   {'name': 'Fast 4G',  'download': 4*1024*1024//8,  'upload': 3*1024*1024//8,  'latency': 20},
    'wifi': {'name': 'WiFi',     'download': 30*1024*1024//8, 'upload': 15*1024*1024//8, 'latency': 2},
    'slow': {'name': 'Slow WiFi','download': 50*1024//8,      'upload': 20*1024//8,      'latency': 800},
}

PERSONAS = {
    # 1. THE HAPPY PATH (Speed & Performance)
    'zoomer': {
        'name': 'Zoomer (Speedster)',
        'desc': 'Tech-savvy user speed-running the signup',
        'typing_delay': 0.05,
        'action_delay': 0.5,
        'hesitation': 0.0,
        'system_prompt': """
            You are an impatient, tech-savvy Gen Z user.
            GOAL: Finish signup in under 10 seconds.
            BEHAVIOR:
            - Do NOT read instructions. 
            - Always choose "Sign up with Google" if available.
            - If a page takes >2 seconds to load, COMPLAIN: "Laggy interface".
            - Ignore "Terms" and "Privacy" links.
        """
    },

    # 2. THE INSIGHT GENERATOR (UX & Copy Analysis)
    'boomer': {
        'name': 'Boomer (The Critic)',
        'desc': 'Anxious first-timer who gets stuck easily',
        'typing_delay': 0.5,
        'action_delay': 4.0,
        'hesitation': 5.0,
        'system_prompt': """
            You are a 65-year-old non-technical user. You are nervous.
            GOAL: Ensure everything is 100% clear before clicking.
            BEHAVIOR:
            - Scroll up and down to read everything.
            - If a label is vague (like just "ID"), STOP and flag "High Confusion".
            - If text is small (<16px) or low contrast, COMPLAIN: "I can't read this".
            - Verify: "Does this button actually look clickable?"
        """
    },

    # 3. THE EDGE CASE (Legal & Link Verification)
    'skeptic': {
        'name': 'The Skeptic',
        'desc': 'Privacy-focused user checking legal pages',
        'typing_delay': 0.2,
        'action_delay': 2.0,
        'hesitation': 2.0,
        'system_prompt': """
            You are a paranoid privacy advocate.
            GOAL: Find security flaws and broken links.
            BEHAVIOR:
            - Refuse Social Logins (Google/FB). Use Email only.
            - Click "Terms of Service" first. If it's a broken link, flag CRITICAL BUG.
            - Look for "Marketing Consent" checkboxes and uncheck them.
        """
    },

    # 4. THE CHAOS MONKEY (Robustness & Form Validation)
    'chaos': {
        'name': 'Chaos Monkey',
        'desc': 'Clumsy user trying to break the form',
        'typing_delay': 0.1,
        'action_delay': 1.0,
        'hesitation': 0.0,
        'system_prompt': """
            You are a clumsy user testing error handling.
            GOAL: Trigger validation errors.
            BEHAVIOR:
            - Click "Next" immediately without filling anything.
            - Enter invalid email formats (e.g., "felicia@" or "test.com").
            - If the app crashes or lets you pass with bad data, flag a BUG.
        """
    },

    # 5. THE CONSTRAINT TESTER (New! - Mobile & Accessibility)
    'mobile': {
        'name': 'Mobile Native',
        'desc': 'User on a small screen with fat fingers',
        'typing_delay': 0.3,
        'action_delay': 1.5,
        'hesitation': 1.0,
        'system_prompt': """
            You are using a smartphone with a cracked screen under bright sunlight.
            GOAL: Test touch targets and readability.
            BEHAVIOR:
            - If buttons are too close together (<10px gap), COMPLAIN: "Fat finger risk".
            - If the keyboard would cover the input field, flag a UI BUG.
            - If you have to scroll horizontally to see content, flag as "Not Mobile Responsive".
        """
    }
}


# ======================================================================
# LLM PLANNER PROMPT - Persona-aware autonomous planning
# ======================================================================

PLANNER_SYSTEM_PROMPT = """You are an autonomous QA agent performing a real user journey on a website.
You act as a specific USER PERSONA and must test the sign-up / registration flow.

Your job:
1. OBSERVE the current page (screenshot + interactive elements list)
2. DECIDE the single best next action to progress toward completing sign-up
3. Return a structured JSON response

RULES:
- Perform ONE action per turn.
- Action types: Tap, Input, Scroll, KeyboardPress, Sleep, GoToPage, GoBack, Hover, Select, SolveCaptcha, WaitForOTP, WaitForMagicLink
- For Tap/Input/Scroll/Hover/Select, reference an element by its numeric ID from the elements list.
- For Input, provide the value to type. Use realistic test data:
  - Email: ai.test.user@example.com
  - Password: SecurePass123!
  - Name: Test User
  - Phone: +1234567890
- Set "done": true when you see:
  * Success/confirmation page ("Account Created", "Welcome", "Verify Email")
  * Final submission confirmation ("You're all set", "Check your email")
  * Error that blocks ALL progress ("Service Unavailable", infinite loading)
  * Stuck in a loop (same action failing 3+ times)
- If you see a cookie consent banner, dismiss it first.
- If you need to scroll to find more elements, use Scroll.
- DO NOT click social login buttons (Google, Apple, Facebook) - use email signup.

CAPTCHA HANDLING (CRITICAL):
- If you see a CAPTCHA (reCAPTCHA, hCaptcha, image puzzle, distorted text), use the SolveCaptcha action:
  {"action": {"type": "SolveCaptcha"}, "observation": "CAPTCHA detected - [type]", ...}
- NOTE: Auto-solving is currently disabled. The SolveCaptcha action will DETECT the CAPTCHA and report it, but it will NOT solve it automatically. The CAPTCHA requires manual human intervention.
- After SolveCaptcha reports the CAPTCHA, continue with the next logical step in the flow. Do NOT keep retrying SolveCaptcha — just note the CAPTCHA as a UX friction issue and move on.
- Do NOT try to manually tap CAPTCHA tiles, Verify, Skip, or any CAPTCHA elements yourself. Just report it and continue.
- If the CAPTCHA blocks form submission, note it as a P1 blocker requiring human action and proceed to the DONE state.

OTP HANDLING:
- If the page says "Enter the code sent to your email" or "Verify your email":
  {"action": {"type": "WaitForOTP"}, "observation": "OTP verification required", ...}
- If the page says "Click the link in your email" or "Verify via email link":
  {"action": {"type": "WaitForMagicLink"}, "observation": "Magic link verification required", ...}
- Do NOT type random numbers into OTP fields. Use the WaitForOTP action.

DROPDOWN/SELECT HANDLING (CRITICAL):
- For country/region selectors, dropdowns, and comboboxes:
  1. First TAP the dropdown element to open it (look for elements like "Select", "Choose", or arrow icons)
  2. Wait for options to appear (they may be in a new list/menu)
  3. Then TAP the specific option you want to select
- If you see a dropdown showing "Select" or a placeholder, TAP it first to reveal options
- After tapping a dropdown, the next step should be tapping the actual country/option
- Look for elements with text like country names, or list items that appeared after opening
- For native <select> elements, use Select action with the option value

COUNTRY SELECTION STRATEGY:
- When selecting a country, first tap the dropdown to open it
- IMPORTANT: Many financial/trading sites RESTRICT certain countries (US, UK, etc). If you search for a country and get "No result found", try a DIFFERENT country immediately!
- ALWAYS pick from VISIBLE countries in the dropdown list. Good options: Indonesia, Malaysia, Singapore, Japan, Germany, France, Australia, Brazil, India
- DO NOT keep retrying the same country if it fails or shows "No result found"
- If a search shows "No result found", clear it and TAP directly on a visible country from the list
- If dropdown has many items, scroll within the dropdown to find options

AVOIDING REPETITION:
- Check PREVIOUS ACTIONS history - do NOT repeat an action that already failed
- If you tried searching for a country and it failed, try a DIFFERENT country or tap a visible option
- If stuck for 2+ steps on the same element, try an alternative approach

RESPONSE FORMAT (valid JSON only, NO markdown fences, NO extra text):
{"observation":"<what you see>","reasoning":"<why this action, from persona perspective>","action":{"type":"Tap","element_id":5,"value":null,"element_description":"Sign up button"},"ux_issues":["issue1"],"confusion_score":2,"done":false,"done_reason":null}

UX ISSUES TO DETECT:
- Form or important elements are below the fold (not visible without scrolling) after clicking a CTA
- No auto-scroll to bring user attention to the expected next step
- Form placement: signup form should be immediately visible after clicking "Create Account" or "Sign Up"
- Confusing layout, unclear next steps, poor contrast, small buttons
- Missing feedback (no loading state, no error messages, no confirmation)

CONFUSION SCORE (rate the CURRENT PAGE, not your action):
- 0-1: Crystal clear, obvious next step
- 2-3: Slightly unclear labels or small buttons
- 4-6: Confusing layout, hard to find elements, unclear flow
- 7-8: Highly confusing, ambiguous options, poor UX
- 9-10: Completely stuck, no clear path forward, page broken

If an action FAILS or nothing changes, increase confusion score on next step!"""


def build_planner_prompt(persona_cfg, device_cfg, elements_json, page_url, page_title, step_num, history):
    history_text = ""
    failure_warning = ""
    
    if history:
        history_text = "\n\nPREVIOUS ACTIONS (learn from failures - DO NOT repeat failed actions):\n"
        failed_count = 0
        for h in history[-5:]:
            status_marker = "⚠️ FAILED" if "FAIL" in h['outcome'] or "No result" in h['outcome'] else "✓"
            history_text += f"  Step {h['step']}: {h['action_desc']} -> {h['outcome']} {status_marker}\n"
            if "FAIL" in h['outcome']:
                failed_count += 1
        
        # Check for repeated failures
        recent_actions = [h['action_desc'] for h in history[-3:]]
        if len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2]:
            history_text += "\n  ⚠️ WARNING: You are repeating the same action! Try something DIFFERENT.\n"
            failure_warning = "\n⚠️ CRITICAL: Last action did nothing or failed. Increase confusion_score (7-10) and try different approach!"
        
        # If last action failed, remind to increase confusion score
        if history and "FAIL" in history[-1].get('outcome', ''):
            failure_warning = "\n⚠️ Last action FAILED - set confusion_score higher (6-9) to reflect the difficulty!"
    
    return f"""CURRENT STATE:
- Step: {step_num}
- URL: {page_url}
- Page Title: {page_title}
- Device: {device_cfg['name']} ({device_cfg['viewport']['width']}x{device_cfg['viewport']['height']})
- Persona: {persona_cfg['name']} -- {persona_cfg['desc']}
- Persona Behavior: {persona_cfg['system_prompt']}
{history_text}{failure_warning}

INTERACTIVE ELEMENTS ON PAGE:
{elements_json}

Decide your SINGLE next action. Respond with valid JSON only."""


# ======================================================================
# RAW ANTHROPIC API HELPERS
# ======================================================================

def _get_anthropic_client():
    """Create a raw Anthropic client."""
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


async def _call_claude_vision(client, system_prompt, user_prompt, images_b64=None, max_tokens=2048):
    """Call Claude with vision via raw Anthropic SDK. Returns response text."""
    content = []
    if images_b64:
        for img in images_b64:
            if img and isinstance(img, str):
                # Strip data URI prefix if present
                raw = img.split('base64,')[1] if 'base64,' in img else img
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": raw},
                })
    content.append({"type": "text", "text": user_prompt})

    delay = 3.0
    for attempt in range(1, 4):
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": content}],
            )
            return msg.content[0].text
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "429" in err or "overloaded" in err:
                print(f"      Rate limited (attempt {attempt}/3), waiting {delay:.0f}s...")
                await asyncio.sleep(delay)
                delay *= 2
                continue
            raise
    return None


def _parse_llm_json(text):
    """Extract JSON from LLM response."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    return None


def _build_action_dict(action_type, element_id, value):
    """Build action dict for ActionExecutor.execute()."""
    action = {"type": action_type, "locate": {}, "param": {}}
    if action_type in ('Tap', 'Hover', 'Scroll'):
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
    elif action_type == 'Input':
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
        action["param"]["value"] = value or ""
        action["param"]["clear_before_type"] = True
    elif action_type == 'Select':
        # Select action for native <select> elements or custom dropdowns
        action["type"] = "Tap"  # Fall back to Tap for custom dropdowns
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
        if value:
            action["param"]["value"] = value  # Option value to select
    elif action_type == 'KeyboardPress':
        action["param"]["value"] = value or "Enter"
    elif action_type == 'Sleep':
        action["param"]["timeMs"] = int(value) if value and str(value).isdigit() else 1000
    elif action_type == 'SolveCaptcha':
        action["type"] = "SolveCaptcha"
        # No element_id needed - CaptchaSolver finds the CAPTCHA itself
    elif action_type == 'WaitForOTP':
        action["type"] = "WaitForOTP"
        action["param"]["sender_filter"] = value or ""  # Optional sender hint
    elif action_type == 'WaitForMagicLink':
        action["type"] = "WaitForMagicLink"
        action["param"]["sender_filter"] = value or ""
    elif action_type == 'GoToPage':
        action["param"]["url"] = value or ""
    return action


async def _show_red_dot(page, element_buffer, element_id):
    """Show red dot on element by crawler ID."""
    try:
        eid = str(element_id)
        elem = element_buffer.get(eid) or element_buffer.get(int(eid), {})
        if elem:
            cx, cy = elem.get('center_x'), elem.get('center_y')
            if cx is not None and cy is not None:
                await page.evaluate(RED_DOT_JS, [int(cx), int(cy)])
                await asyncio.sleep(0.5)
    except Exception:
        pass


async def _diagnose_before_after(client, before_b64, after_b64, action_desc, expectation):
    """Dual-screenshot diagnosis via raw Claude."""
    prompt = f"""Compare BEFORE and AFTER screenshots of a browser action.
Action: {action_desc}
Expected: {expectation}
Respond JSON only: {{"status":"PASSED"|"FAILED"|"PARTIAL","visual_observation":"<what changed>","diagnosis":"<root cause if failed>","severity":"P0 - Critical"|"P1 - Major"|"P2 - Minor"|"P3 - Cosmetic","responsible_team":"Frontend"|"Backend"|"UX/Design"|"N/A"}}"""
    try:
        raw = await _call_claude_vision(
            client,
            "You are a visual QA diagnosis expert. Respond with JSON only.",
            prompt,
            images_b64=[before_b64, after_b64],
            max_tokens=1024,
        )
        return _parse_llm_json(raw)
    except Exception as e:
        print(f"      Diagnosis error: {e}")
        return None


# ======================================================================
# AUTONOMOUS AGENT - Fully powered by webqa_agent + raw Anthropic
# ======================================================================

async def autonomous_signup_test(
    url: str,
    device: str = 'desktop',
    network: str = 'wifi',
    persona: str = 'zoomer',
    locale: str = 'en-US',
    max_steps: int = 10,
    screenshot_callback = None,
    diagnostic_callback = None,
    page_callback = None,
    headless: bool = False,
    test_id: Optional[str] = None,
    captcha_provider: str = 'claude',
) -> Dict[str, Any]:
    """
    Autonomous signup testing -- AI decides every step.
    
    Args:
        screenshot_callback: Optional async callback(screenshot_path, step, action) for streaming
        diagnostic_callback: Optional async callback(step, diagnostic_data) for streaming analysis results

    Uses:
    - BrowserSessionPool: browser lifecycle
    - DeepCrawler: DOM element detection + highlighting
    - ActionHandler + ActionExecutor: action execution
    - ScrollHandler: intelligent scrolling
    - Raw Anthropic API: vision + reasoning
    """
    if not AUTONOMOUS_AVAILABLE:
        print("Autonomous mode not available. Install webqa_agent.")
        return {'status': 'ERROR', 'reason': 'Dependencies missing'}

    device_cfg = DEVICES[device]
    network_cfg = NETWORKS[network]
    persona_cfg = PERSONAS[persona]

    client = _get_anthropic_client()
    if not client:
        print("No API key. Set CLAUDE_API_KEY or ANTHROPIC_API_KEY in backend/.env")
        return {'status': 'ERROR', 'reason': 'No API key'}

    print("\n" + "=" * 70)
    print("SPECTER AUTONOMOUS AGENT (webqa_agent + raw Anthropic)")
    print("=" * 70)
    print(f"  URL: {url}")
    print(f"  Device: {device_cfg['name']}")
    print(f"  Network: {network_cfg['name']}")
    print(f"  Persona: {persona_cfg['name']} -- {persona_cfg['desc']}")
    print(f"  Locale: {locale}")
    print(f"  Max Steps: {max_steps}")
    print("=" * 70 + "\n")

    # -- 1. Browser via BrowserSessionPool --
    browser_config = {
        'browser_type': 'chromium',
        'viewport': device_cfg['viewport'],
        'headless': headless,
        'language': locale,
    }

    pool = BrowserSessionPool(pool_size=1, browser_config=browser_config)
    pool.disable_tab_interception = True   # Allow multi-tab / page navigation
    session = await pool.acquire(browser_config=browser_config)

    # Track test start time for OTP/magic link filtering
    test_start_time = datetime.now()

    try:
        page = session.page

        # Expose the live page object to callers (e.g. live endpoint)
        if page_callback:
            await page_callback(page)

        # Network throttling via CDP
        try:
            cdp = await page.context.new_cdp_session(page)
            await cdp.send('Network.emulateNetworkConditions', {
                'offline': False,
                'downloadThroughput': network_cfg['download'],
                'uploadThroughput': network_cfg['upload'],
                'latency': network_cfg['latency'],
            })
        except Exception as e:
            print(f"  Network throttling skipped: {e}")

        # Network + console log capture
        network_logs: List[Dict] = []
        console_logs: List[str] = []

        def on_response(response):
            if response.status >= 400 or "/api" in response.url:
                network_logs.append({"status": response.status, "url": response.url, "method": response.request.method})

        def on_console(msg):
            if msg.type in ("error", "warning"):
                console_logs.append(f"[{msg.type}] {msg.text}")

        page.on("response", on_response)
        page.on("console", on_console)

        # -- 2. Navigate --
        print(f"Navigating to {url}...")
        await session.navigate_to(url)
        await asyncio.sleep(3)
        print("Page loaded\n")

        # -- 3. Initialize webqa_agent tools --
        # Ensure any prior in-process screenshot session is cleared so each
        # test run creates a fresh, unique report directory.
        ActionHandler.clear_screenshot_session()

        # Prefer initializing the screenshot session directory BEFORE creating
        # the ActionHandler instance to avoid any timing/race conditions.
        # Configure screenshot saving behavior (class-level) BEFORE initializing
        # the session so init will create the desired directory.
        ActionHandler.set_screenshot_config(save_screenshots=True)

        if test_id:
            custom_reports_dir = os.path.join('reports', test_id)
            os.makedirs(custom_reports_dir, exist_ok=True)
            screenshot_dir = ActionHandler.init_screenshot_session(custom_report_dir=custom_reports_dir)
        else:
            screenshot_dir = ActionHandler.init_screenshot_session()
        action_handler = ActionHandler()
        await action_handler.initialize(page)
        reports_dir = str(screenshot_dir.parent)
        os.makedirs(reports_dir, exist_ok=True)
        print(f"Report directory: {reports_dir}")

        executor = ActionExecutor(action_handler)
        await executor.initialize()

        crawler = DeepCrawler(page)
        scroll_handler = ScrollHandler(page)

        # -- 4. Autonomous Loop --
        print(f"AI will decide actions based on persona: {persona_cfg['name']}\n")

        results = []
        history = []
        confusion_scores = []

        for step_num in range(1, max_steps + 1):
            print(f"{'~' * 55}")
            print(f"Step {step_num}/{max_steps}")

            # Persona timing
            if step_num > 1 and persona_cfg['hesitation'] > 0:
                await asyncio.sleep(persona_cfg['hesitation'])
            if step_num > 1:
                await asyncio.sleep(persona_cfg['action_delay'])

            start_time = datetime.now()
            network_logs.clear()
            console_logs.clear()

            try:
                # -- RECOVER: If page was closed (navigation/new tab), get the latest page --
                if page.is_closed():
                    context = session.context
                    if context and context.pages:
                        page = context.pages[-1]
                        session._page = page  # Update session's internal page ref
                        crawler = DeepCrawler(page)
                        scroll_handler = ScrollHandler(page)
                        await action_handler.initialize(page)
                        await executor.initialize()
                        page.on("response", on_response)
                        page.on("console", on_console)
                        print(f"  [Recovery] Switched to new page: {page.url[:80]}")
                        await asyncio.sleep(2)
                    else:
                        print(f"  [Recovery] No pages available in context, stopping")
                        results.append({'step': step_num, 'result': 'ERROR', 'error': 'All pages closed'})
                        break

                # -- OBSERVE: Crawl DOM + Screenshot --
                crawl_result = await crawler.crawl(
                    highlight=True,
                    cache_dom=True,
                    viewport_only=False,
                )

                element_buffer = crawl_result.raw_dict()
                action_handler.set_page_element_buffer(element_buffer)

                elements_json = crawl_result.to_llm_json()

                screenshot_b64, screenshot_path = await action_handler.b64_page_screenshot(
                    file_name=f'step_{step_num:02d}_observe',
                    context='autonomous',
                )

                await crawler.remove_marker()
                
                # Stream screenshot to frontend if callback provided
                # Line 815-827 in main.py
                if screenshot_callback:
                    from pathlib import Path
                    abs_screenshot_path = None
                    try:
                        if screenshot_path:
                            p = Path(screenshot_path)
                            # FIX: Check if path is already absolute OR construct from screenshot_dir
                            if p.is_absolute():
                                abs_screenshot_path = str(p)
                            else:
                                 # Use the full relative path, not just the filename
                                 abs_screenshot_path = str(Path(screenshot_dir) / p)  # Changed from p.name to p
                    except Exception:
                        abs_screenshot_path = str(Path(screenshot_dir) / Path(screenshot_path or '').name)
    
                    await screenshot_callback(abs_screenshot_path, step_num, "Observing page")
                
    
 
                print(f"  📸 Screenshot saved:")
                print(f"     Expected dir: {screenshot_dir}")
                print(f"     Returned path: {screenshot_path}")
                if screenshot_path:
                    print(f"     Path exists: {os.path.exists(screenshot_path)}")
                    print(f"     Is absolute: {Path(screenshot_path).is_absolute()}")
                page_url, page_title = await session.get_url()

                # -- DECIDE: Ask Claude what to do --
                user_prompt = build_planner_prompt(
                    persona_cfg, device_cfg, elements_json,
                    page_url, page_title, step_num, history,
                )

                raw_response = await _call_claude_vision(
                    client,
                    PLANNER_SYSTEM_PROMPT,
                    user_prompt,
                    images_b64=[screenshot_b64] if screenshot_b64 else None,
                    max_tokens=2048,
                )

                plan = _parse_llm_json(raw_response)
                if not plan:
                    print(f"  LLM response not parseable, retrying...")
                    raw_response = await _call_claude_vision(
                        client,
                        PLANNER_SYSTEM_PROMPT,
                        user_prompt + "\n\nCRITICAL: Respond with valid JSON only. No markdown. No extra text.",
                        images_b64=[screenshot_b64] if screenshot_b64 else None,
                        max_tokens=2048,
                    )
                    plan = _parse_llm_json(raw_response)

                if not plan:
                    print(f"  LLM failed to return valid JSON")
                    results.append({'step': step_num, 'result': 'ERROR', 'error': 'Unparseable LLM response'})
                    continue

                observation = plan.get('observation', '')
                reasoning = plan.get('reasoning', '')
                action_plan = plan.get('action', {})
                ux_issues = plan.get('ux_issues', [])
                confusion = plan.get('confusion_score', 0)
                done = plan.get('done', False)

                print(f"  Observe: {observation[:100]}")
                print(f"  Reason:  {reasoning[:100]}")

                if confusion > 0:
                    confusion_scores.append(confusion)
                    label = "HIGH!" if confusion >= 7 else "Moderate" if confusion >= 4 else "Minor"
                    print(f"  Confusion: {confusion}/10 ({label})")

                if ux_issues:
                    for issue in ux_issues[:3]:
                        print(f"  UX Issue: {issue}")

                if done:
                    done_reason = plan.get('done_reason', 'Flow completed')
                    print(f"  DONE: {done_reason}")
                    await action_handler.b64_page_screenshot(file_name=f'step_{step_num:02d}_done', context='autonomous')
                    results.append({'step': step_num, 'result': 'DONE', 'reason': done_reason})
                    break

                # -- ACT: Execute via ActionExecutor --
                action_type = action_plan.get('type', 'Sleep')
                element_id = action_plan.get('element_id')
                value = action_plan.get('value', '')
                element_desc = action_plan.get('element_description', '')

                act_msg = f"  Action: {action_type}"
                if element_id is not None:
                    act_msg += f" #{element_id} ({element_desc})"
                if value and action_type == 'Input':
                    act_msg += f' -> "{value}"'
                print(act_msg)

                if element_id is not None:
                    await _show_red_dot(page, element_buffer, element_id)

                action_dict = _build_action_dict(action_type, element_id, value)
                
                # Handle special CAPTCHA/OTP actions (not routed through ActionExecutor)
                if action_type == 'SolveCaptcha':
                    detector = CaptchaDetector()
                    detection = await detector.detect(page, elements_json, screenshot_b64, client)
                    
                    if detection['has_captcha']:
                        # ── CAPTCHA auto-solving DISABLED ──
                        # The auto-solver code is preserved in captcha_handler.py but
                        # reCAPTCHA consistently detects automation. Instead, we notify
                        # the user/tester that manual human intervention is required.
                        captcha_type = detection['captcha_type']
                        print(f"[CAPTCHA DETECTED] Type: {captcha_type}")
                        print(f"[CAPTCHA] Auto-solving is disabled. This CAPTCHA requires human intervention.")
                        print(f"[CAPTCHA] Please solve the CAPTCHA manually in the browser window, then the test will continue.")
                        
                        success = False
                        exec_msg = (
                            f"CAPTCHA detected ({captcha_type}). "
                            f"Auto-solving is disabled — this CAPTCHA requires manual human action. "
                            f"Please solve it in the browser window."
                        )
                        ux_issues.append(f"CAPTCHA present ({captcha_type}) - requires human intervention")
                        
                        # --- Original auto-solve code (preserved, disabled) ---
                        # ai_provider = captcha_provider or os.getenv('CAPTCHA_AI_PROVIDER', 'claude')
                        # tile_dir = str(screenshot_dir) if screenshot_dir else None
                        # solver = CaptchaSolver(page, claude_client=client, ai_provider=ai_provider, tile_screenshot_dir=tile_dir)
                        # solve_result = await solver.solve(detection['captcha_type'], detection['captcha_selector'], detection.get('instruction_text', ''))
                        # success = solve_result['solved']
                        # exec_msg = f"CAPTCHA {detection['captcha_type']}: {'solved' if success else 'failed'} via {solve_result['method']} ({solve_result['time_taken_ms']}ms)"
                        # ux_issues.append(f"CAPTCHA present ({detection['captcha_type']}) - {solve_result['time_taken_ms']}ms to solve")
                    else:
                        success = True
                        exec_msg = "No CAPTCHA detected"
                
                elif action_type == 'WaitForOTP':
                    otp_email = os.getenv('TEST_EMAIL_ADDRESS')
                    otp_password = os.getenv('TEST_EMAIL_APP_PASSWORD')
                    imap_server = os.getenv('TEST_EMAIL_IMAP_SERVER', 'imap.gmail.com')
                    
                    if not otp_email or not otp_password:
                        success = False
                        exec_msg = "OTP reader not configured (missing TEST_EMAIL_ADDRESS/TEST_EMAIL_APP_PASSWORD in .env)"
                        print(f"[OTP] ERROR: TEST_EMAIL_ADDRESS={'set' if otp_email else 'MISSING'}, TEST_EMAIL_APP_PASSWORD={'set' if otp_password else 'MISSING'}")
                    else:
                        print(f"[OTP] Reading OTP from {otp_email} via {imap_server}")
                        print(f"[OTP] Polling inbox for new emails since test start...")
                        reader = OTPReader(otp_email, otp_password, imap_server=imap_server)
                        sender_filter = value or action_dict.get('param', {}).get('sender_filter')
                        if sender_filter:
                            print(f"[OTP] Filtering by sender: {sender_filter}")
                        
                        try:
                            otp_result = await reader.wait_for_otp(
                                sender_filter=sender_filter,
                                since_timestamp=test_start_time,
                                timeout_seconds=90
                            )
                            
                            if otp_result['found']:
                                otp_code = otp_result['code']
                                print(f"[OTP] Found OTP code: {otp_code} (subject: {otp_result.get('email_subject', 'N/A')})")
                                
                                # Find the OTP input field on the page and type the code
                                # Try common OTP input selectors first
                                otp_input = None
                                otp_selectors = [
                                    'input[name*="otp" i]', 'input[name*="code" i]', 'input[name*="verification" i]',
                                    'input[name*="token" i]', 'input[type="tel"]', 'input[type="number"]',
                                    'input[autocomplete="one-time-code"]',
                                    'input[inputmode="numeric"]',
                                ]
                                for sel in otp_selectors:
                                    try:
                                        otp_input = await page.query_selector(sel)
                                        if otp_input and await otp_input.is_visible():
                                            break
                                        otp_input = None
                                    except Exception:
                                        continue
                                
                                if otp_input:
                                    await otp_input.click()
                                    await asyncio.sleep(0.3)
                                    await otp_input.fill(otp_code)
                                    print(f"[OTP] Typed OTP into detected input field")
                                else:
                                    # Fallback: type into whatever is focused
                                    print(f"[OTP] No specific OTP input found, typing into focused element")
                                    await page.keyboard.type(otp_code)
                                
                                # Brief wait, then try pressing Enter or clicking submit
                                await asyncio.sleep(0.5)
                                # Look for a submit/verify button near the OTP input
                                verify_btn = await page.query_selector(
                                    'button[type="submit"], button:has-text("Verify"), button:has-text("Confirm"), '
                                    'button:has-text("Submit"), button:has-text("Continue"), input[type="submit"]'
                                )
                                if verify_btn and await verify_btn.is_visible():
                                    await verify_btn.click()
                                    print(f"[OTP] Clicked verify/submit button")
                                else:
                                    await page.keyboard.press('Enter')
                                    print(f"[OTP] Pressed Enter to submit OTP")
                                
                                success = True
                                exec_msg = f"OTP entered: {otp_code} (waited {otp_result['wait_time_ms']}ms)"
                                ux_issues.append(f"OTP required - {otp_result['wait_time_ms']}ms wait time")
                            else:
                                success = False
                                exec_msg = f"OTP not received within timeout: {otp_result.get('error', 'timeout')}"
                                print(f"[OTP] {exec_msg}")
                        except Exception as e:
                            success = False
                            exec_msg = f"OTP reader error: {str(e)}"
                            print(f"[OTP] Exception: {e}")
                            import traceback
                            traceback.print_exc()
                
                elif action_type == 'WaitForMagicLink':
                    otp_email = os.getenv('TEST_EMAIL_ADDRESS')
                    otp_password = os.getenv('TEST_EMAIL_APP_PASSWORD')
                    imap_server = os.getenv('TEST_EMAIL_IMAP_SERVER', 'imap.gmail.com')
                    
                    if not otp_email or not otp_password:
                        success = False
                        exec_msg = "Magic link reader not configured (missing TEST_EMAIL_ADDRESS/TEST_EMAIL_APP_PASSWORD in .env)"
                        print(f"[MagicLink] ERROR: TEST_EMAIL_ADDRESS={'set' if otp_email else 'MISSING'}, TEST_EMAIL_APP_PASSWORD={'set' if otp_password else 'MISSING'}")
                    else:
                        print(f"[MagicLink] Reading magic link from {otp_email} via {imap_server}")
                        reader = OTPReader(otp_email, otp_password, imap_server=imap_server)
                        sender_filter = value or action_dict.get('param', {}).get('sender_filter')
                        
                        try:
                            link_result = await reader.wait_for_magic_link(
                                sender_filter=sender_filter,
                                since_timestamp=test_start_time,
                                timeout_seconds=90
                            )
                            
                            if link_result['found']:
                                print(f"[MagicLink] Found link: {link_result['link'][:80]}...")
                                await page.goto(link_result['link'])
                                success = True
                                exec_msg = f"Magic link opened (waited {link_result['wait_time_ms']}ms)"
                                ux_issues.append(f"Magic link required - {link_result['wait_time_ms']}ms wait time")
                            else:
                                success = False
                                exec_msg = f"Magic link not received within timeout: {link_result.get('error', 'timeout')}"
                                print(f"[MagicLink] {exec_msg}")
                        except Exception as e:
                            success = False
                            exec_msg = f"Magic link reader error: {str(e)}"
                            print(f"[MagicLink] Exception: {e}")
                            import traceback
                            traceback.print_exc()
                
                else:
                    # Normal action execution through ActionExecutor
                    exec_result = await executor.execute(action_dict)
                    success = exec_result.get('success', False) if isinstance(exec_result, dict) else bool(exec_result)
                    exec_msg = exec_result.get('message', '') if isinstance(exec_result, dict) else str(exec_result)

                print(f"  Result: {'OK' if success else 'FAIL'} - {exec_msg[:80]}")

                if action_type == 'Input' and value:
                    await asyncio.sleep(len(str(value)) * persona_cfg['typing_delay'])

                end_time = datetime.now()
                dwell_time_ms = int((end_time - start_time).total_seconds() * 1000)

                await asyncio.sleep(1.0)

                # -- AFTER screenshot --
                screenshot_after_b64, screenshot_after_path = await action_handler.b64_page_screenshot(
                    file_name=f'step_{step_num:02d}_after', context='autonomous',
                )

                # -- VERIFY: Dual-screenshot diagnosis --
                dual_diagnosis = None
                if screenshot_b64 and screenshot_after_b64 and screenshot_b64 != screenshot_after_b64:
                    dual_diagnosis = await _diagnose_before_after(
                        client, screenshot_b64, screenshot_after_b64,
                        f"{action_type} on {element_desc}",
                        "Action should progress the sign-up flow",
                    )
                    if dual_diagnosis:
                        print(f"  Diagnosis: {dual_diagnosis.get('status', '?')} - {dual_diagnosis.get('visual_observation', '')[:70]}")

                # Build history
                action_desc_text = f"{action_type}"
                if element_desc:
                    action_desc_text += f" '{element_desc}'"
                if value and action_type == 'Input':
                    action_desc_text += f" = '{value}'"
                outcome = "OK" if success else f"FAIL: {exec_msg[:40]}"
                history.append({'step': step_num, 'action_desc': action_desc_text, 'outcome': outcome})

                # -- HANDOFF to Feature 2 --
                touch_x, touch_y = 0.5, 0.5
                if element_id is not None:
                    eid = str(element_id)
                    elem = element_buffer.get(eid) or element_buffer.get(int(eid), {})
                    if elem:
                        vp = page.viewport_size
                        touch_x = elem.get('center_x', vp['width']//2) / vp['width']
                        touch_y = elem.get('center_y', vp['height']//2) / vp['height']

                handoff = {
                    'step_id': step_num,
                    'persona': f"{persona_cfg['name']} ({device_cfg['name']}, {network_cfg['name']})",
                    'action_taken': f"{action_desc_text} -> {outcome}",
                    'agent_expectation': 'Action progresses the sign-up flow',
                    'outcome': {},
                    'meta_data': {
                        'touch_x': touch_x, 'touch_y': touch_y,
                        'dwell_time_ms': dwell_time_ms,
                        'device_type': device_cfg['name'],
                        'network_type': network_cfg['name'],
                        'locale': locale, 'persona': persona_cfg['name'],
                    },
                    'evidence': {
                        'screenshot_before_path': _resolve_screenshot_path(screenshot_path) if screenshot_path else 'backend/assets/mock_before.jpg',
                        'screenshot_after_path': _resolve_screenshot_path(screenshot_after_path) if screenshot_after_path else 'backend/assets/mock_after.jpg',
                        'network_logs': list(network_logs),
                        'console_logs': list(console_logs),
                        'expected_outcome': 'Action progresses the sign-up flow',
                        'actual_outcome': action_desc_text,
                        'ui_analysis': {
                            'issues': ux_issues,
                            'confusion_score': confusion,
                            'accessibility_score': 0,
                            'elderly_friendly': confusion < 4,
                        },
                        'dual_diagnosis': dual_diagnosis,
                    },
                }

                # Build initial step report (confusion score, ux issues, evidence collected first)
                step_report = {
                    'step_id': step_num,
                    'timestamp': datetime.now().isoformat(),
                    'persona': persona_cfg['name'],
                    'device': device_cfg['name'],
                    'network': network_cfg['name'],
                    'action': action_desc_text,
                    'observation': observation,
                    'reasoning': reasoning,
                    'confusion_score': confusion,
                    'ux_issues': ux_issues,
                    'dwell_time_ms': dwell_time_ms,
                    'outcome': dual_diagnosis if dual_diagnosis else {'status': 'OK' if success else 'FAIL'},
                    'evidence': handoff['evidence'],
                }

                # Feature 2 pipeline - adds diagnosis, severity, team, f_score to handoff['outcome']
                pipeline_result = run_specter_pipeline(handoff)
                
                # Update step_report with enriched outcome (now has diagnosis, severity, team, f_score)
                step_report['outcome'] = handoff.get('outcome', step_report['outcome'])
                
                # Save complete step report with diagnosis
                with open(os.path.join(reports_dir, f"step_{step_num:02d}_report.json"), 'w') as f:
                    json.dump(step_report, f, indent=2)
                
                results.append({
                    'step': step_num, 'action': action_desc_text,
                    'result': pipeline_result, 'dwell_time': dwell_time_ms,
                    'confusion': confusion,
                })
                print(f"  Specter: {pipeline_result}")
                
                # AUTO-STOP DETECTION: Prevent wasted tokens on stuck flows
                if len(results) >= 3:
                    last_3_results = [r['result'] for r in results[-3:]]
                    last_3_actions = [r['action'] for r in results[-3:]]
                    
                    # Stop if stuck in failure loop (3 consecutive failures)
                    if all(result == 'FAIL' for result in last_3_results):
                        print()
                        print("  🛑 AUTO-STOP: 3 consecutive failures detected")
                        print("  Flow appears stuck - stopping early to save tokens")
                        results.append({'step': step_num + 1, 'result': 'DONE', 'reason': 'Auto-stopped: stuck in failure loop'})
                        break
                    
                    # Stop if repeating same action (likely stuck)
                    if last_3_actions[0] == last_3_actions[1] == last_3_actions[2]:
                        print()
                        print("  🛑 AUTO-STOP: Same action repeated 3 times")
                        print(f"  Stuck on: {last_3_actions[0]}")
                        results.append({'step': step_num + 1, 'result': 'DONE', 'reason': 'Auto-stopped: action repetition detected'})
                        break
                
                # Broadcast complete diagnostic data to frontend (after diagnosis)
                if diagnostic_callback:
                    try:
                        await diagnostic_callback(step_num, step_report)
                    except Exception as cb_err:
                        print(f"  Diagnostic callback error: {cb_err}")

            except Exception as e:
                print(f"  Step error: {e}")
                traceback.print_exc()
                results.append({'step': step_num, 'result': 'ERROR', 'error': str(e)})

            print()

    finally:
        await pool.release(session)
        await pool.close_all()

    # -- Summary --
    passed = sum(1 for r in results if r.get('result') in ('PASS', 'DONE'))
    failed = len(results) - passed
    avg_confusion = sum(confusion_scores) / len(confusion_scores) if confusion_scores else 0

    print("=" * 70)
    print("AUTONOMOUS TEST COMPLETE")
    print("=" * 70)
    print(f"  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")
    print(f"  Avg Confusion: {avg_confusion:.1f}/10" +
          (" (High!)" if avg_confusion >= 7 else " (Moderate)" if avg_confusion >= 4 else ""))
    print(f"  Reports: {reports_dir}")
    print("=" * 70)
    
    # 🚨 SEND SUMMARY ALERT ONCE AT END (if there were failures)
    if failed > 0:
        print("\n📊 FINAL ANALYSIS SUMMARY")
        print("=" * 70)
        
        # Collect ALL issues from all steps (not just most severe)
        all_issue_reports = []
        most_severe_report = None
        severity_rank = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        
        for step_file in sorted(os.listdir(reports_dir)):
            if step_file.startswith('step_') and step_file.endswith('_report.json'):
                with open(os.path.join(reports_dir, step_file), 'r') as f:
                    report = json.load(f)
                    outcome = report.get('outcome', {})
                    dual_diag = report.get('evidence', {}).get('dual_diagnosis', {})
                    
                    # Check if there's an issue in EITHER outcome OR dual_diagnosis
                    has_outcome_issue = outcome.get('status') in ['FAILED', 'UX_ISSUE'] and outcome.get('diagnosis')
                    has_dual_diag_issue = dual_diag.get('status') == 'FAILED'
                    
                    if has_outcome_issue or has_dual_diag_issue:
                        # If outcome is empty but dual_diagnosis exists, copy it to outcome for PDF rendering
                        if not outcome.get('diagnosis') and has_dual_diag_issue:
                            report['outcome'] = {
                                'status': dual_diag['status'],
                                'diagnosis': dual_diag.get('diagnosis', ''),
                                'severity': dual_diag.get('severity', 'P2'),
                                'responsible_team': dual_diag.get('responsible_team', 'QA'),
                                'visual_observation': dual_diag.get('visual_observation', ''),
                                'recommendations': []  # dual_diagnosis doesn't have recommendations
                            }
                            outcome = report['outcome']
                        
                        all_issue_reports.append(report)
                        
                        current_severity = outcome.get('severity', 'P3')
                        current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                        
                        if most_severe_report is None:
                            most_severe_report = report
                        else:
                            best_rank = severity_rank.get(most_severe_report['outcome'].get('severity', 'P3').split(' - ')[0], 3)
                            if current_rank < best_rank:
                                most_severe_report = report
        
        # Group issues by team and send separate PDFs to each team
        if all_issue_reports:
            try:
                # Group reports by responsible team
                from collections import defaultdict
                issues_by_team = defaultdict(list)
                overall_most_severe = all_issue_reports[0]
                
                for report in all_issue_reports:
                    team = report['outcome'].get('responsible_team', 'QA')
                    issues_by_team[team].append(report)
                    
                    # Track overall most severe for frontend update
                    current_severity = report['outcome'].get('severity', 'P3')
                    best_severity = overall_most_severe['outcome'].get('severity', 'P3')
                    current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                    best_rank = severity_rank.get(best_severity.split(' - ')[0], 3)
                    if current_rank < best_rank:
                        overall_most_severe = report
                
                print(f"  📊 Issues found: {len(all_issue_reports)} steps across {len(issues_by_team)} teams")
                teams_alerted = list(issues_by_team.keys())
                
                # Send separate alert to each team with only their issues
                for team, team_issues in issues_by_team.items():
                    # Find most severe issue for this team
                    team_most_severe = team_issues[0]
                    for issue in team_issues[1:]:
                        current_severity = issue['outcome'].get('severity', 'P3')
                        best_severity = team_most_severe['outcome'].get('severity', 'P3')
                        current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                        best_rank = severity_rank.get(best_severity.split(' - ')[0], 3)
                        if current_rank < best_rank:
                            team_most_severe = issue
                    
                    # Build handoff packet for this team ONLY
                    handoff_for_alert = {
                        'step_id': team_most_severe['step_id'],
                        'persona': team_most_severe['persona'],
                        'action_taken': team_most_severe['action'],
                        'agent_expectation': 'Complete signup flow',
                        'outcome': team_most_severe['outcome'],
                        'evidence': team_most_severe['evidence'],
                        'meta_data': {
                            'device_type': team_most_severe['device'],
                            'network_type': team_most_severe['network']
                        },
                        'all_issues': team_issues  # Only this team's issues
                    }
                    
                    severity = team_most_severe['outcome'].get('severity', 'P2')
                    diagnosis = team_most_severe['outcome'].get('diagnosis', 'Issues detected')
                    
                    print(f"  🚨 Sending alert to {team} team")
                    print(f"     Issues: {len(team_issues)} step(s), Severity: {severity}")
                    print(f"     Diagnosis: {diagnosis[:80]}...")
                    
                    try:
                        success = send_alert(handoff_for_alert)
                        if success:
                            print(f"  ✅ {team} PDF sent to their Slack channel")
                        else:
                            print(f"  ⚠️ {team} alert failed or no evidence; PDF generation attempted")
                    except Exception as e:
                        print(f"  ⚠️ send_alert raised exception: {e}")
                
                # Send final diagnostic update to indicate alert has been sent
                if diagnostic_callback:
                    try:
                        # Update the most severe report to indicate completion
                        teams_text = ', '.join(teams_alerted)
                        completion_update = {
                            **overall_most_severe,
                            'outcome': {
                                **overall_most_severe['outcome'],
                                'diagnosis': f"{overall_most_severe['outcome'].get('diagnosis', '')}\n\n✅ Analysis completed - PDFs sent to {teams_text} team(s)",
                                'alert_sent': True,
                                'analysis_complete': True
                            }
                        }
                        await diagnostic_callback(overall_most_severe['step_id'], completion_update)
                        print(f"  📤 Frontend updated with completion status")
                    except Exception as cb_err:
                        print(f"  Diagnostic callback error: {cb_err}")
                
            except Exception as e:
                print(f"  ⚠️  Alert failed: {e}")
                if "channel_not_found" in str(e):
                    print(f"  💡 Solution: Invite bot to channel with /invite @Specter Bot")
        
        print("=" * 70 + "\n")
    else:
        print("  ✅ No alerts needed - all steps passed!")
        
        # Send completion update to frontend
        if diagnostic_callback and len(results) > 0:
            try:
                # Send a success completion message for the last step
                last_step = results[-1]['step']
                completion_msg = {
                    'step_id': last_step,
                    'timestamp': datetime.now().isoformat(),
                    'outcome': {
                        'status': 'SUCCESS',
                        'diagnosis': '✅ Analysis completed - All steps passed successfully',
                        'analysis_complete': True,
                        'f_score': 0,
                        'severity': 'P3 - Cosmetic'
                    },
                    'evidence': {},
                    'confusion_score': 0
                }
                await diagnostic_callback(last_step, completion_msg)
                print(f"  📤 Frontend updated with completion status")
            except Exception as cb_err:
                print(f"  Diagnostic callback error: {cb_err}")
        
        print("=" * 70 + "\n")

    return {
        'status': 'PASS' if failed == 0 else 'FAIL',
        'device': device, 'network': network, 'persona': persona,
        'steps': results, 'passed': passed, 'failed': failed,
        'avg_confusion_score': round(avg_confusion, 2),
        'reports_dir': reports_dir,
    }


# ======================================================================
# SPECTER PIPELINE - Feature 2: Diagnosis Engine
# ======================================================================

def run_specter_pipeline(handoff_packet: Dict[str, Any]) -> str:
    print(f"  Checking Step {handoff_packet['step_id']}...")
    result = check_expectation(handoff_packet)

    # Check if there are UX issues even if test passed
    ux_issues = handoff_packet.get('evidence', {}).get('ui_analysis', {}).get('issues', [])
    has_ux_issues = len(ux_issues) > 0

    if result['status'] == "SUCCESS" and not has_ux_issues:
        return "PASS"
    
    # If there are UX issues but test passed, create a UX-focused alert (but don't send yet)
    if result['status'] == "SUCCESS" and has_ux_issues:
        handoff_packet['outcome'] = {
            "status": "UX_ISSUE",
            "visual_observation": f"UX issues detected: {', '.join(ux_issues[:2])}",
            "f_score": result.get('f_score', 100),
            "calculated_severity": "P2 - Minor",  # UX-only issues are typically P2
            "gif_path": result.get('gif_path'),
            "heatmap_path": result.get('heatmap_path'),
        }
        final_packet = diagnose_failure(handoff_packet, use_vision=True)
        
        # Mark for alert but don't send yet (will send at end of test)
        responsible_team = final_packet.get('outcome', {}).get('responsible_team', 'Design')
        print(f"  ⚠️  UX Issues ({len(ux_issues)}) detected - Will alert {responsible_team} team at test end")
        
        return "PASS_WITH_UX_ISSUES"

    handoff_packet['outcome'] = {
        "status": "FAILED",
        "visual_observation": result['reason'],
        "f_score": result.get('f_score'),
        "calculated_severity": result.get('calculated_severity'),
        "gif_path": result.get('gif_path'),
        "heatmap_path": result.get('heatmap_path'),
    }

    final_packet = diagnose_failure(handoff_packet, use_vision=True)
    
    # Mark issue but don't send alert yet (will send summary at test end)
    severity = final_packet.get('outcome', {}).get('severity', '')
    responsible_team = final_packet.get('outcome', {}).get('responsible_team', 'Unknown')
    print(f"   Issue detected: {severity} - {responsible_team} team (Alert queued for end)")
    
    return "FAIL"


# ======================================================================
# CLI INTERFACE
# ======================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Specter: Autonomous AI QA Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://deriv.com/signup
  python main.py https://example.com --persona boomer --device iphone13
  python main.py https://example.com --network 3g --max-steps 20
        """
    )
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--persona', default='zoomer', choices=PERSONAS.keys())
    parser.add_argument('--device', default='desktop', choices=DEVICES.keys())
    parser.add_argument('--network', default='wifi', choices=NETWORKS.keys())
    parser.add_argument('--locale', default='en-US')
    parser.add_argument('--max-steps', type=int, default=15)
    return parser.parse_args()


async def main_async():
    args = parse_args()
    os.makedirs("backend/assets", exist_ok=True)
    return await autonomous_signup_test(
        url=args.url, device=args.device, network=args.network,
        persona=args.persona, locale=args.locale, max_steps=args.sps,
    )


def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    result = asyncio.run(main_async())
    sys.exit(0 if result.get('status') in ('PASS', 'SUCCESS', 'DONE') else 1)


if __name__ == "__main__":
    main()
