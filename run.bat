@echo off
title OpenEnv Peak
echo.
echo ╔══════════════════════════════════════════╗
echo ║       OpenEnv Peak — Windows Runner      ║
echo ╚══════════════════════════════════════════╝
echo.

:: Check Python
python --version 2>NUL
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo Download from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)

:: Install deps
echo Installing dependencies...
python -m pip install fastapi uvicorn[standard] pydantic httpx python-multipart -q
if %errorlevel% neq 0 (
    echo.
    echo ERROR: pip install failed. Trying with --user flag...
    python -m pip install fastapi "uvicorn[standard]" pydantic httpx python-multipart -q --user
)

:: Run
echo.
echo Starting server at http://127.0.0.1:7860
echo Open your browser to: http://127.0.0.1:7860
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 7860
pause
