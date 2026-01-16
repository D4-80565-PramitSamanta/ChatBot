#!/usr/bin/env python3
"""Start script for Railway deployment"""
import os
import uvicorn

# Get PORT from environment or use default
port = int(os.getenv("PORT", 8000))

print(f"🚀 Starting ZentrumHub server on port {port}...")

# Start uvicorn programmatically
uvicorn.run("app.main:app", host="0.0.0.0", port=8080)
