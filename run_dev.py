"""Dev server launcher — forces ProactorEventLoop on Windows so Playwright works."""
import uvicorn
import sys

if __name__ == "__main__":
    # On Windows we need ProactorEventLoop for Playwright. With loop="none" uvicorn
    # uses the default policy (ProactorEventLoop). With reload=True on Windows the
    # reloader passes the listening socket to a child process, which triggers
    # WinError 87 (IOCP + inherited socket). So on Windows we disable reload.
    is_windows = sys.platform == "win32"
    use_reload = not is_windows

    if is_windows:
        print("🚀 Specter Dev Server (Windows: no auto-reload; restart manually after code changes)")
    else:
        print("🚀 Specter Dev Server (reload enabled)")
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=use_reload,
        loop="none",
    )
