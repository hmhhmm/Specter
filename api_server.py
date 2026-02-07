"""FastAPI server to expose Specter backend functionality."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import json
import os
from typing import Optional, List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert

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

class TestConfig(BaseModel):
    url: str
    device: str = "desktop"
    network: str = "wifi"
    persona: str = "normal"
    max_steps: int = 4

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
        # Import needed modules
        import sys
        import os
        import asyncio
        from pathlib import Path
        
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
        
        # Create callback for screenshot streaming
        async def screenshot_callback(screenshot_path: str, step: int, action: str):
            """Called when a new screenshot is captured."""
            try:
                # Read screenshot and convert to base64
                import base64
                with open(screenshot_path, 'rb') as f:
                    screenshot_data = base64.b64encode(f.read()).decode('utf-8')
                
                await manager.broadcast({
                    "type": "step_update",
                    "test_id": test_id,
                    "step": step,
                    "action": action,
                    "screenshot": f"data:image/png;base64,{screenshot_data}"
                })
            except Exception as e:
                print(f"Error broadcasting screenshot: {e}")
        
        # Run autonomous test with streaming
        result = await autonomous_signup_test(
            url=config.url,
            device=config.device,
            network=config.network,
            persona=config.persona,
            max_steps=config.max_steps,
            screenshot_callback=screenshot_callback,
            headless=True
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


@app.post("/api/test/start")
async def start_test(config: TestConfig, background_tasks: BackgroundTasks):
    """Start a new autonomous test."""
    try:
        # Check if webqa_agent is available
        try:
            from webqa_agent.browser.session import BrowserSessionPool
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

if __name__ == "__main__":
    import uvicorn
    print("Starting Specter API Server...")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
