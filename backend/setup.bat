@echo off
REM CompareKart Backend Setup Script (Windows)

echo.
echo 🚀 CompareKart Backend Setup
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create database
echo.
echo 🗄️  Initializing database...
python -c "from database import init_db; init_db(); print('✅ Database initialized')"

REM Summary
echo.
echo ==============================
echo ✨ Setup Complete!
echo ==============================
echo.
echo To start the backend:
echo   1. Activate environment: venv\Scripts\activate.bat
echo   2. Run server: python main.py
echo.
echo Access API at: http://localhost:8000
echo View docs at: http://localhost:8000/docs
echo.
pause
