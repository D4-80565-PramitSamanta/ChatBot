#!/bin/bash
# FastAPI Chatbot Server Startup Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo "Starting FastAPI server on port 8080..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
