@echo off
setlocal enabledelayedexpansion
title AI Excel Assistant - 1-Click Starter

echo =====================================================================
echo           AI EXCEL ASSISTANT - 1-CLICK LAUNCHER
echo   Python + FastAPI + SQL + LLM + Spreadsheet Processing
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python 3.10 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Check or create virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [*] Virtual environment created successfully.
)

:: 3. Check and install dependencies
if not exist ".venv\Lib\site-packages\fastapi" (
    echo [*] Installing required packages from requirements.txt...
    echo [*] (This only happens on first launch, please wait a minute)
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Package installation failed!
        pause
        exit /b 1
    )
)

:: 4. Ensure environment file exists
if not exist ".env" (
    echo [*] Creating .env file from .env.example...
    copy .env.example .env >nul
)

:: 5. Ensure sample dataset exists
if not exist "sample_data\sample_sales_data.xlsx" (
    echo [*] Generating sample Excel dataset...
    .\.venv\Scripts\python sample_data\create_sample_excel.py
)

:: 6. Launch browser in 2 seconds in background
echo [*] Launching web browser at http://127.0.0.1:8000 ...
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: 7. Start Uvicorn FastAPI Server
echo.
echo =====================================================================
echo   SERVER STARTED SUCCESSFULLY!
echo   Web UI:        http://127.0.0.1:8000
echo   Swagger Docs:  http://127.0.0.1:8000/docs
echo   Press CTRL+C anytime to stop the server.
echo =====================================================================
echo.

.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
