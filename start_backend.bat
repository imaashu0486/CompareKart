@echo off
REM CompareKart Backend - Quick Start (Windows)
REM Save as: start_backend.bat

echo CompareKart Backend - Quick Start
echo ==================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo.❌ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
) else (
    echo.✅ Virtual environment found
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Start backend
echo.
echo Starting CompareKart backend...
echo ==================================
echo API will be available at: http://localhost:8000
echo API Docs:                 http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
pause
