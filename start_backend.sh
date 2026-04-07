#!/bin/bash
# CompareKart Backend - Developer Quick Start
# Save as: start_backend.sh (Linux/Mac) or start_backend.bat (Windows)

echo "CompareKart Backend - Quick Start"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/.venv/bin/activate

# Start backend
echo ""
echo "Starting CompareKart backend..."
echo "================================"
echo "API will be available at: http://localhost:8000"
echo "API Docs:                 http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
