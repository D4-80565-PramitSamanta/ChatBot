#!/usr/bin/env python3
"""Start script for Railway deployment"""
import uvicorn

# Hardcoded port
port = 8080

print(f"🚀 Starting ZentrumHub server on port {port}...")

# Start uvicorn programmatically
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
