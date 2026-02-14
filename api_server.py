"""FastAPI server to expose Specter backend functionality."""

# CRITICAL: Windows fix for Playwright - MUST be before any imports
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
from typing import Optional, List
from pathlib import Path
import base64
from webqa_agent.browser.session import BrowserSessionPool

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert
from backend.root_cause_intelligence import RootCauseIntelligence

app = FastAPI(title="Specter API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active test sessions
active_tests = {}

# Maps test_id -> the real Playwright Page object used by the running test.
# This is what the live WebSocket reads from via CDP.
active_sessions: dict = {}

class TestConfig(BaseModel):
    url: str
    device: str = "desktop"
    network: str = "wifi"
    persona: str = "normal"  # Always fast normal user
    max_steps: int = 5
    captcha_strategy: str = "auto"      # "auto" | "detect_only" | "skip"
    captcha_provider: str = "openai"    # "claude" | "openai" | "gemini" - recommend openai for cost savings
    otp_sender_filter: str = ""          # e.g., "Deriv" to filter emails

class TestResult(BaseModel):
    step_id: str
    status: str
    f_score: Optional[float] = None
    severity: Optional[str] = None
    diagnosis: Optional[str] = None
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    gif_path: Optional[str] = None

# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"status": "Specter API is running", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "backend": "connected"}


async def run_test_background(test_id: str, config: TestConfig):
    """Run autonomous test in background and broadcast updates."""
    try:
        
        
        # Add parent directory to path if not already there
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from main import autonomous_signup_test
        
        # Broadcast test started
        await manager.broadcast({
            "type": "test_started",
            "test_id": test_id,
            "url": config.url
        })
        
        # Create callback for screenshot and diagnostic streaming
        async def screenshot_callback(screenshot_path: str, step: int, action: str):
            """Called when a new screenshot is captured."""
            try:
                # Attempt to read screenshot and convert to base64. Try multiple locations
                import base64
                screenshot_data = None
                step_data = None

                # Try up to a few times to allow file writes to complete
                attempts = 3
                for attempt in range(attempts):
                    try_path = screenshot_path
                    if os.path.exists(try_path):
                        with open(try_path, 'rb') as f:
                            screenshot_data = base64.b64encode(f.read()).decode('utf-8')
                        break

                    # If not found, attempt to locate under a reports/*/screenshots folder
                    try:
                        path_parts = screenshot_path.replace('\\', '/').split('/')
                        if 'reports' in path_parts:
                            reports_idx = path_parts.index('reports')
                            reports_dir = os.path.join(*path_parts[:reports_idx+2])
                        else:
                            # Fallback: try to find any recent reports folder
                            reports_dir = None

                        if reports_dir:
                            candidate = os.path.join(reports_dir, 'screenshots', os.path.basename(screenshot_path))
                            if os.path.exists(candidate):
                                with open(candidate, 'rb') as f:
                                    screenshot_data = base64.b64encode(f.read()).decode('utf-8')
                                break
                    except Exception:
                        pass

                    # Small delay before retrying
                    await asyncio.sleep(0.25)

                # Try to read a step report JSON for diagnostic metadata if present
                try:
                    # Derive reports dir if possible and read the corresponding step report
                    path_parts = screenshot_path.replace('\\', '/').split('/')
                    if 'reports' in path_parts:
                        reports_idx = path_parts.index('reports')
                        reports_dir = '/'.join(path_parts[:reports_idx+2])
                    else:
                        reports_dir = None

                    if reports_dir:
                        step_report_path = os.path.join(reports_dir, f"step_{step:02d}_report.json")
                        if os.path.exists(step_report_path):
                            with open(step_report_path, 'r', encoding='utf-8') as f:
                                step_report = json.load(f)
                                outcome = step_report.get("outcome", {})
                                severity = outcome.get("severity", "")
                                alert_sent = severity in ['P0 - Critical', 'P1 - Major'] and outcome.get("status") == "FAILED"
                                step_data = {
                                    "confusion_score": step_report.get("confusion_score", 0),
                                    "network_logs": step_report.get("evidence", {}).get("network_logs", [])[:3],
                                    "f_score": outcome.get("f_score"),
                                    "diagnosis": outcome.get("diagnosis"),
                                    "severity": severity,
                                    "responsible_team": outcome.get("responsible_team"),
                                    "ux_issues": step_report.get("ux_issues", [])[:3],
                                    "alert_sent": alert_sent
                                }
                except Exception:
                    step_data = step_data or None

                payload = {
                    "type": "step_update",
                    "test_id": test_id,
                    "step": step,
                    "action": action,
                    "screenshot": f"data:image/png;base64,{screenshot_data}" if screenshot_data else None,
                    "stepData": step_data
                }

                await manager.broadcast(payload)
            except Exception as e:
                # Don't raise on transient screenshot issues; log and continue
                print(f"Error broadcasting screenshot (non-fatal): {e}")
        
        # Create callback for diagnostic data streaming after analysis
        async def diagnostic_callback(step: int, step_report: dict):
            """Called when step analysis completes with full diagnostic data."""
            try:
                outcome = step_report.get("outcome", {})
                evidence = step_report.get("evidence", {})
                
                # Check if this issue was escalated to Slack
                # Alert is sent for: FAILED status OR UX_ISSUE status (with diagnosis)
                severity = outcome.get("severity", "")
                status = outcome.get("status", "")
                alert_sent = (status in ["FAILED", "UX_ISSUE"]) and severity and outcome.get("diagnosis")
                
                diagnostic_data = {
                    "confusion_score": step_report.get("confusion_score", 0),
                    "network_logs": evidence.get("network_logs", [])[:5],
                    "console_logs": evidence.get("console_logs", [])[:3],
                    "f_score": outcome.get("f_score"),
                    "diagnosis": outcome.get("diagnosis"),
                    "severity": severity,
                    "responsible_team": outcome.get("responsible_team"),
                    "ux_issues": step_report.get("ux_issues", [])[:3],
                    "alert_sent": outcome.get("alert_sent", False),
                    "analysis_complete": outcome.get("analysis_complete", False),
                    "dwell_time_ms": step_report.get("dwell_time_ms", 0)
                }
                
                await manager.broadcast({
                    "type": "diagnostic_update",
                    "test_id": test_id,
                    "step": step,
                    "diagnosticData": diagnostic_data
                })
            except Exception as e:
                print(f"Error broadcasting diagnostic data: {e}")
        
        # Page callback: store the real Playwright page for live streaming
        async def page_callback(page):
            """Called by autonomous_signup_test once the browser page is ready."""
            active_sessions[test_id] = page
            print(f"[LiveStream] Page stored for test {test_id}")

        # Run autonomous test with streaming
        result = await autonomous_signup_test(
            url=config.url,
            device=config.device,
            network=config.network,
            persona=config.persona,
            max_steps=config.max_steps,
            screenshot_callback=screenshot_callback,
            diagnostic_callback=diagnostic_callback,
            page_callback=page_callback,
            headless=True,
            test_id=test_id,
        )
        
        # Update test status
        active_tests[test_id]["status"] = "completed"
        active_tests[test_id]["result"] = result
        
        # Broadcast completion
        await manager.broadcast({
            "type": "test_complete",
            "test_id": test_id,
            "results": {
                "status": result.get("status"),
                "passed": result.get("passed"),
                "failed": result.get("failed"),
                "steps": result.get("steps", []),
                "reports_dir": result.get("reports_dir")
            }
        })
        
    except Exception as e:
        active_tests[test_id]["status"] = "failed"
        active_tests[test_id]["error"] = str(e)
        
        await manager.broadcast({
            "type": "test_error",
            "test_id": test_id,
            "error": str(e)
        })
    finally:
        # Clean up stored page reference
        active_sessions.pop(test_id, None)


@app.post("/api/test/start")
async def start_test(config: TestConfig, background_tasks: BackgroundTasks):
    """Start a new autonomous test."""
    try:
        # Check if webqa_agent is available
        try:
            
            autonomous_available = True
        except ImportError:
            autonomous_available = False
            
        if not autonomous_available:
            raise HTTPException(
                status_code=400, 
                detail="Autonomous mode requires webqa_agent. Install via: pip install webqa-agent"
            )
        
        # Generate test ID
        import time
        test_id = f"test_{int(time.time())}"
        
        # Store test config
        active_tests[test_id] = {
            "config": config.model_dump(),
            "status": "running",
            "steps": [],
            "result": None,
            "error": None
        }
        
        # Run test in background
        background_tasks.add_task(run_test_background, test_id, config)
        
        return {"test_id": test_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test/{test_id}")
async def get_test_status(test_id: str):
    """Get test status and results."""
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return active_tests[test_id]

@app.get("/api/reports/{path:path}")
async def get_report_file(path: str):
    """Serve report files (screenshots, GIFs, etc.)."""
    # Try both relative and absolute paths
    possible_paths = [
        os.path.join("reports", path),
        path,
        os.path.join("backend", "assets", path)
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time test updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/live/{test_id}")
async def live_stream(websocket: WebSocket, test_id: str):
    """Stream the REAL test browser viewport to the frontend.

    Tries CDP Page.startScreencast first. If no CDP frames arrive
    within 3 seconds, falls back to polling page.screenshot() so
    the live view always works (headless or headed, any Playwright
    version).

    Protocol:
      1. Client connects.
      2. Server waits (up to 30 s) for the page to appear in active_sessions.
      3. Attempts CDP screencast; falls back to screenshot polling.
      4. Every frame is forwarded as {"frame": "data:image/jpeg;base64,..."}.
      5. Client sends "stop" or disconnects to end.
    """
    await websocket.accept()
    
    # Check if test is already completed
    test_info = active_tests.get(test_id)
    if test_info and test_info["status"] in ["completed", "failed"]:
        await websocket.send_json({"error": "Test already completed"})
        await websocket.close(code=1000, reason="Test already completed")
        return
    
    cdp = None
    use_polling = False

    try:
        # ---- Wait for the page to become available ----
        page = None
        for _ in range(60):                          # 30 s max wait (60 × 0.5)
            page = active_sessions.get(test_id)
            if page is not None:
                break
            await asyncio.sleep(0.5)

        if page is None:
            await websocket.send_json({"error": "Timeout waiting for browser session"})
            return

        # ---- Try CDP screencast first ----
        frame_count = 0
        cdp_frame_received = asyncio.Event()

        try:
            cdp = await page.context.new_cdp_session(page)
            print(f"[LiveStream] CDP session opened for {test_id}")

            async def _send_cdp_frame(params):
                nonlocal frame_count
                try:
                    await websocket.send_json({
                        "frame": f"data:image/jpeg;base64,{params['data']}"
                    })
                    await cdp.send("Page.screencastFrameAck",
                                   {"sessionId": params["sessionId"]})
                    frame_count += 1
                    cdp_frame_received.set()
                    if frame_count % 30 == 1:
                        print(f"[LiveStream] CDP frame #{frame_count} for {test_id}")
                except Exception as exc:
                    print(f"[LiveStream] CDP frame send error: {exc}")

            def on_frame(params):
                asyncio.ensure_future(_send_cdp_frame(params))

            cdp.on("Page.screencastFrame", on_frame)

            await cdp.send("Page.startScreencast", {
                "format": "jpeg",
                "quality": 60,
                "everyNthFrame": 1,
            })
            print(f"[LiveStream] Screencast started for {test_id}")

            # Wait up to 3 s for the first CDP frame
            try:
                await asyncio.wait_for(cdp_frame_received.wait(), timeout=3.0)
                print(f"[LiveStream] CDP screencast is working for {test_id}")
            except asyncio.TimeoutError:
                print(f"[LiveStream] No CDP frames after 3 s, switching to polling for {test_id}")
                use_polling = True
                try:
                    await cdp.send("Page.stopScreencast")
                    await cdp.detach()
                except Exception:
                    pass
                cdp = None

        except Exception as cdp_err:
            print(f"[LiveStream] CDP failed ({cdp_err}), using polling for {test_id}")
            use_polling = True
            cdp = None

        # ---- Polling fallback: capture page.screenshot() at ~5 fps ----
        if use_polling:
            print(f"[LiveStream] Starting polling mode for {test_id}")
            stop_event = asyncio.Event()

            async def _receive_stop():
                try:
                    while not stop_event.is_set():
                        try:
                            msg = await asyncio.wait_for(
                                websocket.receive_text(), timeout=0.5
                            )
                            if msg == "stop":
                                stop_event.set()
                                return
                        except asyncio.TimeoutError:
                            continue
                except (WebSocketDisconnect, Exception):
                    stop_event.set()

            recv_task = asyncio.ensure_future(_receive_stop())

            try:
                while not stop_event.is_set():
                    if test_id not in active_sessions:
                        break
                    try:
                        raw = await page.screenshot(type="jpeg", quality=60)
                        b64 = base64.b64encode(raw).decode("utf-8")
                        await websocket.send_json({
                            "frame": f"data:image/jpeg;base64,{b64}"
                        })
                        frame_count += 1
                        if frame_count % 30 == 1:
                            print(f"[LiveStream] Poll frame #{frame_count} for {test_id}")
                    except Exception as shot_err:
                        print(f"[LiveStream] Screenshot error: {shot_err}")
                    await asyncio.sleep(0.2)  # ~5 fps
            finally:
                stop_event.set()
                recv_task.cancel()
            return  # polling path exits here

        # ---- CDP path: keep alive until client disconnects ----
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(
                        websocket.receive_text(), timeout=1.0
                    )
                    if msg == "stop":
                        break
                except asyncio.TimeoutError:
                    if test_id not in active_sessions:
                        break
        except WebSocketDisconnect:
            pass

    except WebSocketDisconnect:
        print(f"[LiveStream] Client disconnected ({test_id})")
    except Exception as e:
        print(f"[LiveStream] Error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        if cdp:
            try:
                await cdp.send("Page.stopScreencast")
                await cdp.detach()
            except Exception:
                pass


# ======================================================================
# REPORTS & INCIDENTS API
# ======================================================================

def parse_report_folder(folder_path: str) -> dict:
    """Parse a report folder and extract incident data."""
    folder_name = os.path.basename(folder_path)
    incidents = []
    total_f_score = 0
    step_count = 0
    
    # Find all step report JSON files
    for filename in os.listdir(folder_path):
        if filename.startswith("step_") and filename.endswith("_report.json"):
            report_path = os.path.join(folder_path, filename)
            try:
                with open(report_path, 'r') as f:
                    step_data = json.load(f)
                    
                # Extract incident from step data
                outcome = step_data.get('outcome', {})
                evidence = step_data.get('evidence', {})
                ux_insight = step_data.get('ux_insight', {})
                
                f_score = outcome.get('f_score', 50)
                confusion_score = step_data.get('confusion_score', 0)  # Extract confusion score
                total_f_score += f_score
                step_count += 1
                
                # Determine severity based on F-score
                if f_score >= 80:
                    severity = "P0"
                elif f_score >= 60:
                    severity = "P1"
                elif f_score >= 40:
                    severity = "P2"
                else:
                    severity = "P3"
                
                # Only create incidents that have real diagnosis or critical issues
                diagnosis = outcome.get('diagnosis')
                has_console_errors = evidence.get('console_logs') and len(evidence.get('console_logs', [])) > 0
                has_ux_issues = ux_insight.get('issues') and len(ux_insight.get('issues', [])) > 0
                
                # Skip if no real issue detected (no diagnosis, no errors, low f-score)
                if not diagnosis and not has_console_errors and not has_ux_issues and f_score < 60:
                    continue
                
                # Build incident from step data
                incident = {
                    "id": f"{folder_name[-4:]}_{step_data.get('step_id', 0):02d}",
                    "severity": severity,
                    "title": diagnosis or step_data.get('action_taken', 'Issue Detected'),
                    "device": step_data.get('device', 'Unknown Device'),
                    "confidence": min(95, max(60, 100 - f_score + 50)),
                    "revenueLoss": int((100 - f_score) * 100 * (4 if severity == "P0" else 2 if severity == "P1" else 1)),
                    "cloudPosition": {"x": 50, "y": 50},
                    "monologue": _generate_monologue(step_data),
                    "step_id": step_data.get('step_id'),
                    "timestamp": step_data.get('timestamp'),
                    "f_score": f_score,
                    "confusion_score": confusion_score,
                    "screenshot_before": evidence.get('screenshot_before_path'),
                    "screenshot_after": evidence.get('screenshot_after_path'),
                    "ux_issues": ux_insight.get('issues', []),
                    "network_logs": evidence.get('network_logs', []),
                    "console_logs": evidence.get('console_logs', []),
                    "action_taken": step_data.get('action_taken'),
                    "expectation": step_data.get('agent_expectation'),
                    "responsible_team": outcome.get('responsible_team', 'QA'),
                }
                incidents.append(incident)
            except Exception as e:
                print(f"Error parsing report {report_path}: {e}")
    
    return {
        "folder": folder_name,
        "incidents": incidents,
        "avg_f_score": total_f_score / step_count if step_count > 0 else 0,
        "step_count": step_count
    }

def _generate_monologue(step_data: dict) -> str:
    """Generate AI-style monologue from step data."""
    ux_insight = step_data.get('ux_insight', {})
    evidence = step_data.get('evidence', {})
    outcome = step_data.get('outcome', {})
    
    issues = ux_insight.get('issues', [])
    action = step_data.get('action_taken', 'Unknown action')
    expectation = step_data.get('agent_expectation', 'Expected outcome')
    
    monologue_parts = []
    
    if issues:
        monologue_parts.append(f"Detected {len(issues)} UX issues during analysis.")
        monologue_parts.append(f"Primary concerns: {'; '.join(issues[:2])}")
    
    monologue_parts.append(f"Action performed: {action}")
    monologue_parts.append(f"Expected: {expectation}")
    
    if not ux_insight.get('elderly_friendly', True):
        monologue_parts.append("Warning: Interface not optimized for elderly users.")
    
    if ux_insight.get('accessibility_score', 100) < 70:
        monologue_parts.append(f"Accessibility score: {ux_insight.get('accessibility_score')}/100 - below threshold.")
    
    return " ".join(monologue_parts)


@app.get("/api/incidents")
async def list_incidents(limit: int = 50):
    """List all incidents from report folders."""
    reports_dir = "reports"
    all_incidents = []
    
    if not os.path.exists(reports_dir):
        return {"incidents": [], "total": 0}
    
    # Get all test folders sorted by date (newest first)
    folders = sorted(
        [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
        reverse=True
    )
    
    for folder in folders[:20]:  # Limit to 20 most recent folders
        folder_path = os.path.join(reports_dir, folder)
        report_data = parse_report_folder(folder_path)
        all_incidents.extend(report_data['incidents'])
    
    # Sort by severity (P0 first) then by f_score
    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    all_incidents.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x.get('f_score', 0)))
    
    return {
        "incidents": all_incidents[:limit],
        "total": len(all_incidents)
    }


@app.get("/api/reports/list")
async def list_reports():
    """List all test report folders."""
    reports_dir = "reports"
    
    if not os.path.exists(reports_dir):
        return {"reports": [], "total": 0}
    
    folders = sorted(
        [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
        reverse=True
    )
    
    reports = []
    for folder in folders:
        folder_path = os.path.join(reports_dir, folder)
        report_data = parse_report_folder(folder_path)
        reports.append({
            "id": folder,
            "timestamp": folder,
            "incident_count": len(report_data['incidents']),
            "avg_f_score": report_data['avg_f_score'],
            "step_count": report_data['step_count']
        })
    
    return {"reports": reports, "total": len(reports)}


@app.get("/api/reports/details/{report_id:path}")
async def get_report_details(report_id: str):
    """Get detailed report for a specific test run."""
    report_path = os.path.join("reports", report_id)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_data = parse_report_folder(report_path)
    return report_data


# ======================================================================
# DASHBOARD STATS API
# ======================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get aggregated stats for the command dashboard."""
    reports_dir = "reports"
    
    if not os.path.exists(reports_dir):
        return {
            "total_incidents": 0,
            "total_revenue_leak": 0,
            "avg_f_score": 0,
            "severity_breakdown": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
            "recent_tests": 0,
            "healing_active": False,
            "ai_briefing": "No test data available. Run your first autonomous test to begin analysis.",
            "regional_data": [],
            "competitor_benchmark": 75,
            "f_score_history": []
        }
    
    folders = sorted(
        [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
        reverse=True
    )
    
    all_incidents = []
    f_score_history = []
    
    for folder in folders[:20]:
        folder_path = os.path.join(reports_dir, folder)
        report_data = parse_report_folder(folder_path)
        all_incidents.extend(report_data['incidents'])
        if report_data['avg_f_score'] > 0:
            f_score_history.append({
                "timestamp": folder,
                "score": report_data['avg_f_score']
            })
    
    # Calculate severity breakdown
    severity_breakdown = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    total_revenue_leak = 0
    total_f_score = 0
    
    for incident in all_incidents:
        severity = incident.get('severity', 'P3')
        severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        total_revenue_leak += incident.get('revenueLoss', 0)
        total_f_score += incident.get('f_score', 0)
    
    avg_f_score = total_f_score / len(all_incidents) if all_incidents else 0
    
    # Generate AI briefing based on data
    if severity_breakdown['P0'] > 0:
        ai_briefing = f"Critical friction detected. {severity_breakdown['P0']} P0 incidents require immediate attention. ${total_revenue_leak:,} recovery in progress via Autonomous Remediation."
    elif severity_breakdown['P1'] > 0:
        ai_briefing = f"High-priority issues found. {severity_breakdown['P1']} P1 incidents affecting user experience. Estimated ${total_revenue_leak:,} annual revenue impact."
    else:
        ai_briefing = f"System stable. {len(all_incidents)} minor issues detected. Average F-Score: {avg_f_score:.1f}/100."
    
    return {
        "total_incidents": len(all_incidents),
        "total_revenue_leak": total_revenue_leak,
        "avg_f_score": avg_f_score,
        "severity_breakdown": severity_breakdown,
        "recent_tests": len(folders),
        "healing_active": severity_breakdown['P0'] > 0 or severity_breakdown['P1'] > 0,
        "ai_briefing": ai_briefing,
        "regional_data": [
            {"region": "NA", "issues": severity_breakdown['P0'] + severity_breakdown['P1']},
            {"region": "EU", "issues": severity_breakdown['P2']},
            {"region": "APAC", "issues": severity_breakdown['P3']}
        ],
        "competitor_benchmark": 75,
        "f_score_history": f_score_history[-10:]  # Last 10 data points
    }


# ======================================================================
# DIAGNOSIS & ALERT API
# ======================================================================

class DiagnoseRequest(BaseModel):
    incident_id: str
    screenshot_path: Optional[str] = None
    use_vision: bool = True

class AlertRequest(BaseModel):
    incident_id: str
    severity: str
    title: str
    diagnosis: Optional[str] = None


@app.post("/api/diagnose")
async def diagnose_incident(request: DiagnoseRequest):
    """Trigger AI diagnosis for a specific incident."""
    try:
        # Build a handoff packet for diagnosis
        handoff_packet = {
            "persona": "AI Tester",
            "action_taken": f"Analyzing incident {request.incident_id}",
            "agent_expectation": "Identify root cause and recommend fix",
            "meta_data": {
                "device_type": "Unknown",
                "network_type": "wifi"
            },
            "evidence": {
                "network_logs": [],
                "console_logs": [],
                "screenshot_after_path": request.screenshot_path or ""
            },
            "outcome": {
                "f_score": 50,
                "calculated_severity": "P2"
            }
        }
        
        # Run diagnosis
        result = diagnose_failure(handoff_packet, use_vision=request.use_vision)
        
        return {
            "incident_id": request.incident_id,
            "diagnosis": result.get('outcome', {}).get('diagnosis', 'Unable to diagnose'),
            "severity": result.get('outcome', {}).get('severity', 'P2'),
            "responsible_team": result.get('outcome', {}).get('responsible_team', 'Unknown'),
            "recommendations": result.get('outcome', {}).get('recommendations', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alert")
async def send_alert_notification(request: AlertRequest):
    """Send alert to Slack for an incident."""
    try:
        # Build packet for alert
        final_packet = {
            "evidence": {
                "network_logs": [f"Incident {request.incident_id}: {request.title}"],
                "screenshot_after_path": ""
            },
            "outcome": {
                "severity": request.severity,
                "diagnosis": request.diagnosis or request.title,
                "visual_observation": request.title,
                "f_score": 50,
                "gif_path": None
            }
        }
        
        send_alert(final_packet)
        
        return {
            "status": "sent",
            "incident_id": request.incident_id,
            "message": f"Alert sent for {request.severity} incident"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# ROOT CAUSE INTELLIGENCE API
# ======================================================================

@app.get("/api/incidents/{incident_id}/root-cause")
async def get_root_cause_analysis(incident_id: str):
    """Get root cause analysis for a specific incident."""
    try:
        # Find the report containing this incident
        reports_dir = "reports"
        
        if not os.path.exists(reports_dir):
            raise HTTPException(status_code=404, detail="No reports found")
        
        # Parse incident_id to extract folder reference
        incident_prefix = incident_id[:4]  # e.g., "3666" from "3666_01"
        
        # Find matching report
        for folder in os.listdir(reports_dir):
            if folder.endswith(incident_prefix) or incident_prefix in folder:
                folder_path = os.path.join(reports_dir, folder)
                if not os.path.isdir(folder_path):
                    continue
                
                # Read report data
                for file in os.listdir(folder_path):
                    if file.endswith('_report.json'):
                        report_path = os.path.join(folder_path, file)
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        
                        # Perform root cause analysis
                        rc_intel = RootCauseIntelligence(reports_dir)
                        analysis = rc_intel.analyze_with_root_cause(report_data)
                        
                        return {
                            "incident_id": incident_id,
                            "current_issue": analysis['current_issue'],
                            "similar_issues": analysis['similar_issues'],
                            "is_recurring": analysis['is_recurring'],
                            "recurrence_count": analysis['recurrence_count'],
                            "pattern_detected": analysis['pattern_detected']
                        }
        
        raise HTTPException(status_code=404, detail="Incident not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/root-cause/patterns")
async def get_recurring_patterns():
    """Get all recurring pattern analysis across all incidents."""
    try:
        reports_dir = "reports"
        rc_intel = RootCauseIntelligence(reports_dir)
        
        if not os.path.exists(reports_dir):
            return {"patterns": [], "total": 0}
        
        # Analyze all reports for patterns
        pattern_map = {}  # Key: error_type_component, Value: count
        
        folders = sorted(
            [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
            reverse=True
        )
        
        for folder in folders[:20]:  # Last 20 test runs
            folder_path = os.path.join(reports_dir, folder)
            for file in os.listdir(folder_path):
                if file.endswith('_report.json'):
                    report_path = os.path.join(folder_path, file)
                    try:
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        
                        signature = rc_intel.extract_issue_signature(report_data)
                        key = f"{signature['error_type']}_{signature['component_affected']}"
                        
                        if key not in pattern_map:
                            pattern_map[key] = {
                                "pattern": signature,
                                "count": 0,
                                "test_runs": []
                            }
                        
                        pattern_map[key]["count"] += 1
                        pattern_map[key]["test_runs"].append(folder)
                    except Exception as e:
                        print(f"Error reading {report_path}: {e}")
                        continue
        
        # Filter patterns that occurred more than once
        recurring_patterns = [
            {
                "pattern_id": key,
                "error_type": data["pattern"]["error_type"],
                "component": data["pattern"]["component_affected"],
                "occurrences": data["count"],
                "test_runs": data["test_runs"][:5],  # Show first 5
                "team": data["pattern"]["responsible_team"]
            }
            for key, data in pattern_map.items()
            if data["count"] > 1
        ]
        
        # Sort by occurrences
        recurring_patterns.sort(key=lambda x: x["occurrences"], reverse=True)
        
        return {
            "patterns": recurring_patterns,
            "total": len(recurring_patterns),
            "total_analyzed": len(folders)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# HEALING SUGGESTIONS API
# ======================================================================

@app.get("/api/healing/suggestions")
async def get_healing_suggestions():
    """Get AI-generated healing suggestions based on recent incidents."""
    # Get recent incidents
    reports_dir = "reports"
    suggestions = []
    
    if not os.path.exists(reports_dir):
        return {"suggestions": [], "total": 0}
    
    folders = sorted(
        [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
        reverse=True
    )
    
    # Analyze recent incidents for patterns
    all_issues = []
    for folder in folders[:5]:
        folder_path = os.path.join(reports_dir, folder)
        report_data = parse_report_folder(folder_path)
        for incident in report_data['incidents']:
            all_issues.extend(incident.get('ux_issues', []))
    
    # Generate suggestions based on common issues
    issue_counts = {}
    for issue in all_issues:
        issue_lower = issue.lower()
        if 'button' in issue_lower and 'small' in issue_lower:
            key = "button_size"
        elif 'elderly' in issue_lower or 'text' in issue_lower:
            key = "font_size"
        elif 'loading' in issue_lower or 'spinner' in issue_lower:
            key = "loading_state"
        elif 'contrast' in issue_lower or 'color' in issue_lower:
            key = "contrast"
        else:
            key = "other"
        issue_counts[key] = issue_counts.get(key, 0) + 1
    
    # Generate code suggestions
    if issue_counts.get('button_size', 0) > 0:
        suggestions.append({
            "id": "btn-1",
            "file": "globals.css",
            "type": "style",
            "description": "Increase button touch target for mobile",
            "code_before": ".btn-primary {\n  min-height: 32px;\n  padding: 8px 16px;\n}",
            "code_after": ".btn-primary {\n  min-height: 44px;\n  padding: 12px 24px;\n}",
            "impact": f"Affects {issue_counts.get('button_size', 0)} detected issues"
        })
    
    if issue_counts.get('font_size', 0) > 0:
        suggestions.append({
            "id": "font-1",
            "file": "globals.css",
            "type": "style",
            "description": "Increase base font size for accessibility",
            "code_before": "body {\n  font-size: 12px;\n  line-height: 1.4;\n}",
            "code_after": "body {\n  font-size: 16px;\n  line-height: 1.6;\n}",
            "impact": f"Affects {issue_counts.get('font_size', 0)} detected issues"
        })
    
    if issue_counts.get('contrast', 0) > 0:
        suggestions.append({
            "id": "contrast-1",
            "file": "globals.css",
            "type": "style",
            "description": "Improve button contrast for visibility",
            "code_before": ".checkout-button {\n  color: var(--gray-mute);\n}",
            "code_after": ".checkout-button {\n  color: var(--emerald-glow);\n  box-shadow: 0 0 20px rgba(16,185,129,0.2);\n}",
            "impact": f"Affects {issue_counts.get('contrast', 0)} detected issues"
        })
    
    if issue_counts.get('loading_state', 0) > 0:
        suggestions.append({
            "id": "loading-1",
            "file": "components/Button.tsx",
            "type": "component",
            "description": "Add loading state feedback",
            "code_before": "<button onClick={handleClick}>\n  {children}\n</button>",
            "code_after": "<button onClick={handleClick} disabled={isLoading}>\n  {isLoading ? <Spinner /> : children}\n</button>",
            "impact": f"Affects {issue_counts.get('loading_state', 0)} detected issues"
        })
    
    return {
        "suggestions": suggestions,
        "total": len(suggestions),
        "analysis_summary": {
            "total_issues": len(all_issues),
            "categorized": issue_counts
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Specter API Server...")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
