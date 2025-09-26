#!/usr/bin/env bash

# Setup script for AIPython FastAPI project

echo "🚀 Setting up AIPython FastAPI project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is not supported. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_db.py

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed database with sample data
echo "🌱 Seeding database with sample data..."
python scripts/seed_data.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "API documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "Happy coding! 🚀"
