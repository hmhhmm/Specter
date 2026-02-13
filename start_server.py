"""Startup script for Specter backend with Windows Playwright fix."""
import sys
import asyncio

# CRITICAL: Set event loop policy BEFORE importing any async libraries
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
