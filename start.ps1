# =====================================================================
# AI EXCEL ASSISTANT - 1-CLICK POWERSHELL LAUNCHER
# =====================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "          AI EXCEL ASSISTANT - 1-CLICK LAUNCHER" -ForegroundColor Yellow
Write-Host "  Python + FastAPI + SQL + LLM + Spreadsheet Processing" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found in your PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://python.org and check 'Add to PATH'."
    Read-Host "Press Enter to exit..."
    exit 1
}

# 2. Check Virtual Environment
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[*] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 3. Check Dependencies
if (-not (Test-Path ".\.venv\Lib\site-packages\fastapi")) {
    Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
}

# 4. Check .env
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

# 5. Open Browser
Write-Host "[*] Launching browser at http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

# 7. Start Server
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  SERVER IS RUNNING!" -ForegroundColor Green
Write-Host "  Web Application:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Interactive Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
