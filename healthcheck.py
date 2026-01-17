#!/usr/bin/env python3
"""Health check script for Railway deployment"""
import os
import sys

print("=" * 50)
print("RAILWAY DEPLOYMENT HEALTH CHECK")
print("=" * 50)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   PORT: {os.getenv('PORT', 8000)}")
print(f"   GEMINI_API_KEY: {'SET ✅' if os.getenv('GEMINI_API_KEY') else 'NOT SET ❌'}")

# Check if app can be imported
print("\n2. App Import Check:")
try:
    from app.main import app
    print("   ✅ App imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import app: {e}")
    sys.exit(1)

# Check if config is loaded
print("\n3. Config Check:")
try:
    from app.config import config
    print(f"   HOST: {config.HOST}")
    print(f"   PORT: {config.PORT}")
    print(f"   GEMINI_API_KEY: {'SET ✅' if config.GEMINI_API_KEY else 'NOT SET ❌'}")
except Exception as e:
    print(f"   ❌ Failed to load config: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ All checks passed!")
print("=" * 50)
