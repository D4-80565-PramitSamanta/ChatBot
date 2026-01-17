#!/usr/bin/env python
"""Test script to verify all recipe pages are accessible"""

import httpx
import asyncio

BASE_URL = "https://docs-hotel.prod.zentrumhub.com/recipes"

RECIPE_PAGES = [
    "search-init",
    "search-results",
    "search-results-polling",
    "roomsandrates",
    "pricebyrecommendation",
    "book",
    "blocking-search",
    "zentrum-connect-download-content",
    "zentrum-connect-hotel-search",
    "zentrum-connect-room-rates",
    "zentrum-connect-price",
    "zentrum-connect-book",
    "zentrum-connect-retreive-booking",
    "cancel-booking",
    "zentrum-connect-rate-combinability"
]

async def test_recipe_pages():
    """Test all recipe pages are accessible"""
    
    print("=" * 80)
    print("TESTING RECIPE PAGES ACCESSIBILITY")
    print("=" * 80)
    
    results = {
        "accessible": [],
        "not_accessible": [],
        "errors": []
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, page in enumerate(RECIPE_PAGES, 1):
            url = f"{BASE_URL}/{page}"
            print(f"\n[{i}/{len(RECIPE_PAGES)}] Testing: {page}")
            print(f"    URL: {url}")
            
            try:
                response = await client.get(url)
                
                if response.status_code == 200:
                    content_length = len(response.text)
                    print(f"    ✓ Status: {response.status_code}")
                    print(f"    ✓ Content Length: {content_length} bytes")
                    results["accessible"].append({
                        "page": page,
                        "url": url,
                        "content_length": content_length
                    })
                else:
                    print(f"    ✗ Status: {response.status_code}")
                    results["not_accessible"].append({
                        "page": page,
                        "url": url,
                        "status": response.status_code
                    })
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                results["errors"].append({
                    "page": page,
                    "url": url,
                    "error": str(e)
                })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✓ Accessible: {len(results['accessible'])}/{len(RECIPE_PAGES)}")
    print(f"✗ Not Accessible: {len(results['not_accessible'])}/{len(RECIPE_PAGES)}")
    print(f"⚠ Errors: {len(results['errors'])}/{len(RECIPE_PAGES)}")
    
    if results["not_accessible"]:
        print("\n❌ NOT ACCESSIBLE PAGES:")
        for item in results["not_accessible"]:
            print(f"  - {item['page']} (Status: {item['status']})")
    
    if results["errors"]:
        print("\n⚠️ ERROR PAGES:")
        for item in results["errors"]:
            print(f"  - {item['page']}: {item['error']}")
    
    if len(results["accessible"]) == len(RECIPE_PAGES):
        print("\n🎉 ALL RECIPE PAGES ARE ACCESSIBLE!")
    
    print("\n" + "=" * 80)

async def test_chatbot_recipe_queries():
    """Test chatbot with recipe-specific queries"""
    
    print("\n" + "=" * 80)
    print("TESTING CHATBOT WITH RECIPE QUERIES")
    print("=" * 80)
    
    test_queries = [
        "How do I initialize a search?",
        "What is the search polling workflow?",
        "How to get rooms and rates?",
        "Explain price by recommendation",
        "What is blocking search?",
        "How to download static content?",
        "Explain rate combinability",
        "How to retrieve a booking?",
        "What is the booking workflow?"
    ]
    
    chatbot_url = "http://localhost:8000/api/chat"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check if chatbot is running
        try:
            health_response = await client.get("http://localhost:8000/api/health")
            if health_response.status_code != 200:
                print("\n⚠️ Chatbot is not running. Skipping chatbot tests.")
                print("   Start the server with: python -m uvicorn app.main:app --reload --port 8000")
                return
        except:
            print("\n⚠️ Chatbot is not running. Skipping chatbot tests.")
            print("   Start the server with: python -m uvicorn app.main:app --reload --port 8000")
            return
        
        print("\n✓ Chatbot is running. Testing queries...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"[{i}/{len(test_queries)}] Query: {query}")
            
            try:
                response = await client.post(
                    chatbot_url,
                    json={
                        "question": query,
                        "conversation_id": "test-recipes",
                        "history": []
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✓ Confidence: {data['confidence']}")
                    print(f"    ✓ Sources: {len(data['sources'])} documents")
                    if data['sources']:
                        print(f"    ✓ Source URL: {data['sources'][0]['url']}")
                else:
                    print(f"    ✗ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
            
            print()

if __name__ == "__main__":
    asyncio.run(test_recipe_pages())
    asyncio.run(test_chatbot_recipe_queries())
