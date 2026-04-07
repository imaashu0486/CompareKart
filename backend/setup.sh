#!/bin/bash
# CompareKart Backend Setup Script

echo "🚀 CompareKart Backend Setup"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from database import init_db; init_db(); print('✅ Database initialized')"

# Summary
echo ""
echo "=============================="
echo "✨ Setup Complete!"
echo "=============================="
echo ""
echo "To start the backend:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run server: python main.py"
echo ""
echo "Access API at: http://localhost:8000"
echo "View docs at: http://localhost:8000/docs"
echo ""
