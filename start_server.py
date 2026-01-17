#!/usr/bin/env python3
"""Start script for Railway deployment"""
import uvicorn

# Port for Lovable frontend compatibility
port = 8000

print(f"🚀 Starting ZentrumHub server on port {port}...")

# Start uvicorn programmatically
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
