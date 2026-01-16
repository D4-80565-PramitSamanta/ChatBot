#!/usr/bin/env python
"""Test script for feedback endpoints"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_feedback_flow():
    """Test complete feedback flow"""
    
    print("=" * 80)
    print("TESTING FEEDBACK ENDPOINTS")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test 1: Submit positive feedback
        print("\n[TEST 1] Submit Positive Feedback")
        print("-" * 80)
        
        positive_feedback = {
            "message_id": "test-msg-001",
            "conversation_id": "test-conv-001",
            "question": "How do I search for hotels?",
            "answer": "To search for hotels, use the Search API...",
            "feedback": "positive",
            "confidence": "high",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/analytics/feedback",
                json=positive_feedback
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"  Message: {data['message']}")
                print(f"  Message ID: {data['message_id']}")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
        
        # Test 2: Submit negative feedback
        print("\n[TEST 2] Submit Negative Feedback")
        print("-" * 80)
        
        negative_feedback = {
            "message_id": "test-msg-002",
            "conversation_id": "test-conv-002",
            "question": "how to cancel a booking",
            "answer": "To cancel a booking, you must use the Cancel API...",
            "feedback": "negative",
            "confidence": "high",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/analytics/feedback",
                json=negative_feedback
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"  Message: {data['message']}")
                print(f"  Message ID: {data['message_id']}")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
        
        # Test 3: Get feedback stats
        print("\n[TEST 3] Get Feedback Statistics")
        print("-" * 80)
        
        try:
            response = await client.get(f"{BASE_URL}/api/analytics/feedback-stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"\n📊 FEEDBACK STATISTICS:")
                print(f"  Total Feedback: {data['total_feedback']}")
                print(f"  Positive: {data['positive']}")
                print(f"  Negative: {data['negative']}")
                print(f"  Positive Rate: {data['positive_rate']}%")
                print(f"\n📝 Recent Feedback ({len(data['recent_feedback'])} entries):")
                for i, fb in enumerate(data['recent_feedback'][:5], 1):
                    print(f"    {i}. [{fb['feedback'].upper()}] {fb['question'][:50]}...")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
        
        # Test 4: Get negative feedback
        print("\n[TEST 4] Get Negative Feedback")
        print("-" * 80)
        
        try:
            response = await client.get(f"{BASE_URL}/api/analytics/negative-feedback?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                print(f"\n⚠️ NEGATIVE FEEDBACK ({len(data['negative_feedback'])} entries):")
                for i, fb in enumerate(data['negative_feedback'], 1):
                    print(f"\n  {i}. Question: {fb['question']}")
                    print(f"     Message ID: {fb['message_id']}")
                    print(f"     Timestamp: {fb['timestamp']}")
                    print(f"     Answer Preview: {fb['answer'][:100]}...")
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

async def test_health():
    """Test health endpoint first"""
    print("Checking server health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                print(f"✓ Server is running: {response.json()}")
                return True
            else:
                print(f"✗ Server returned {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print(f"\nPlease start the server first:")
        print(f"  python -m uvicorn app.main:app --reload --port 8000")
        return False

async def main():
    """Main test runner"""
    if await test_health():
        print()
        await test_feedback_flow()
    else:
        print("\n❌ Server is not running. Please start it first.")

if __name__ == "__main__":
    asyncio.run(main())
