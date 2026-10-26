"""
Excel AI Assistant - Main Application Entrypoint
Supports running directly via:
    python main.py
    uvicorn main:app --host 0.0.0.0 --port 8000
Automatically detects and switches to .venv Python if executed under system Python.
"""
import os
import sys
import subprocess

# Configure utf-8 stdout/stderr safely for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Auto-switch to .venv python if running under global/system python without required packages
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
if os.path.exists(VENV_PYTHON):
    current_python = os.path.abspath(sys.executable).lower()
    target_python = os.path.abspath(VENV_PYTHON).lower()
    if current_python != target_python:
        try:
            import fastapi
            import sqlalchemy
        except ImportError:
            # Re-invoke current script using .venv python interpreter
            cmd = [VENV_PYTHON] + sys.argv
            sys.exit(subprocess.call(cmd))

# 3. Import the FastAPI app instance from app.main
from app.main import app

# 4. Direct script execution handler
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"🚀 Starting Excel AI Assistant on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
