#!/usr/bin/env python
"""Test script for /api/explain endpoint"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_explain_endpoint():
    """Test the explain endpoint with various error codes"""
    
    test_cases = [
        {
            "name": "Error 4001 - Validation Error",
            "input_type": "error_code",
            "content": "Error 4001: Request validation failed"
        },
        {
            "name": "Error 4004 - Sold Out",
            "input_type": "error_code",
            "content": "4004"
        },
        {
            "name": "Error 4005 - Price Changed",
            "input_type": "error_code",
            "content": "Error 4005: The price has changed since your last search"
        },
        {
            "name": "Error 5000 - System Error",
            "input_type": "error_code",
            "content": "5000"
        },
        {
            "name": "Generic Error Message",
            "input_type": "error_message",
            "content": "The booking failed with an unknown error"
        }
    ]
    
    print("=" * 80)
    print("TESTING /api/explain ENDPOINT")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[TEST {i}/{len(test_cases)}] {test_case['name']}")
            print("-" * 80)
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/explain",
                    json={
                        "input_type": test_case["input_type"],
                        "content": test_case["content"],
                        "client_id": "test-client"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✓ Status: {response.status_code}")
                    print(f"\n📝 SUMMARY:")
                    print(f"   {data['summary']}")
                    
                    print(f"\n📋 DETAILS ({len(data['details'])} items):")
                    for j, detail in enumerate(data['details'], 1):
                        print(f"   {j}. {detail}")
                    
                    print(f"\n🔧 RECOMMENDED ACTIONS ({len(data['recommended_actions'])} items):")
                    for j, action in enumerate(data['recommended_actions'], 1):
                        print(f"   {j}. {action}")
                    
                    print(f"\n📚 SOURCES ({len(data['sources'])} items):")
                    for source in data['sources']:
                        print(f"   - {source['title']}")
                        print(f"     URL: {source['url']}")
                    
                    print(f"\n🎯 CONFIDENCE: {data['confidence']}")
                    
                else:
                    print(f"✗ Status: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"✗ Exception: {str(e)}")
            
            print()
    
    print("=" * 80)
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
        await test_explain_endpoint()
    else:
        print("\n❌ Server is not running. Please start it first.")

if __name__ == "__main__":
    asyncio.run(main())
