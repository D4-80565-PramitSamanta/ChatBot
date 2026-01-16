#!/usr/bin/env python
"""Test script to verify server configuration"""

print("Testing imports...")

try:
    from app.config import config
    print("✓ Config imported")
    print(f"  - API Key present: {'Yes' if config.GEMINI_API_KEY else 'No'}")
    print(f"  - Knowledge base path: {config.KNOWLEDGE_BASE_PATH}")
except Exception as e:
    print(f"✗ Config error: {e}")
    exit(1)

try:
    from app.llm.gemini_client import GeminiClient
    print("✓ GeminiClient imported")
except Exception as e:
    print(f"✗ GeminiClient error: {e}")
    exit(1)

try:
    from app.services.rag_service import RAGService
    print("✓ RAGService imported")
except Exception as e:
    print(f"✗ RAGService error: {e}")
    exit(1)

try:
    from app.controllers import chat_controller
    print("✓ ChatController imported")
except Exception as e:
    print(f"✗ ChatController error: {e}")
    exit(1)

try:
    from app.main import app
    print("✓ FastAPI app imported")
except Exception as e:
    print(f"✗ FastAPI app error: {e}")
    exit(1)

print("\n✓ All imports successful!")
print("\nNow try running:")
print("  python -m uvicorn app.main:app --reload --port 8000")
