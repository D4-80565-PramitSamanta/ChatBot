#!/usr/bin/env python
"""Quick test for /api/feedback alias endpoint"""

import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_feedback_alias():
    """Test that /api/feedback works as an alias"""
    
    print("=" * 80)
    print("TESTING /api/feedback ALIAS ENDPOINT")
    print("=" * 80)
    
    # Check server health
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get(f"{BASE_URL}/api/health")
            if health.status_code != 200:
                print("\n❌ Server is not running!")
                print("Start with: python -m uvicorn app.main:app --reload --port 8000")
                return
    except:
        print("\n❌ Cannot connect to server!")
        print("Start with: python -m uvicorn app.main:app --reload --port 8000")
        return
    
    print("\n✓ Server is running\n")
    
    # Test data matching the frontend request
    feedback_data = {
        "message_id": "c56ab562-7667-46fa-bfc3-7018defa0ffd",
        "conversation_id": "07ea9810-3b29-4b54-890c-d0acef50f8f7",
        "question": "tell me about base rate and total rate",
        "answer": "Based on the documentation provided...",
        "feedback": "positive",
        "confidence": "high",
        "timestamp": "2026-01-16T18:48:03.096Z"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Original endpoint
        print("[TEST 1] POST /api/analytics/feedback")
        print("-" * 80)
        try:
            response = await client.post(
                f"{BASE_URL}/api/analytics/feedback",
                json=feedback_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Response: {data}")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
        
        print()
        
        # Test 2: Alias endpoint (what frontend uses)
        print("[TEST 2] POST /api/feedback (ALIAS)")
        print("-" * 80)
        
        # Modify message_id for second test
        feedback_data["message_id"] = "test-alias-" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/feedback",
                json=feedback_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Response: {data}")
                print(f"\n✅ ALIAS ENDPOINT WORKS!")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
                print(f"\n❌ ALIAS ENDPOINT FAILED!")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            print(f"\n❌ ALIAS ENDPOINT FAILED!")
        
        print()
        
        # Test 3: Verify feedback was saved
        print("[TEST 3] GET /api/analytics/feedback-stats")
        print("-" * 80)
        try:
            response = await client.get(f"{BASE_URL}/api/analytics/feedback-stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Total Feedback: {data['total_feedback']}")
                print(f"✓ Positive: {data['positive']}")
                print(f"✓ Negative: {data['negative']}")
                print(f"✓ Positive Rate: {data['positive_rate']}%")
                
                if data['total_feedback'] >= 2:
                    print(f"\n✅ FEEDBACK WAS SAVED!")
                else:
                    print(f"\n⚠️ Expected at least 2 feedback entries")
            else:
                print(f"✗ Status: {response.status_code}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
    print("\n💡 Frontend should now use: POST /api/feedback")
    print("   (Both /api/feedback and /api/analytics/feedback work)")

if __name__ == "__main__":
    asyncio.run(test_feedback_alias())
