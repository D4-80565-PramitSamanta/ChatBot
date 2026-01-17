#!/usr/bin/env python
"""Test script for reference documentation fetching"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"
REFERENCE_BASE = "https://docs-hotel.prod.zentrumhub.com/reference"

# Test queries that should fetch from reference docs
TEST_QUERIES = [
    {
        "query": "What fields are required in the rooms and rates request body?",
        "expected_source": "reference",
        "description": "Should fetch API reference for field details"
    },
    {
        "query": "How do I create a booking request?",
        "expected_source": "reference",
        "description": "Should fetch booking API reference"
    },
    {
        "query": "What parameters does the search API accept?",
        "expected_source": "reference",
        "description": "Should fetch search API reference"
    },
    {
        "query": "Show me the request schema for rooms and rates",
        "expected_source": "reference",
        "description": "Should fetch reference for schema details"
    },
    {
        "query": "What is the format of the cancel booking request?",
        "expected_source": "reference",
        "description": "Should fetch cancel API reference"
    },
    {
        "query": "Explain the booking workflow",
        "expected_source": "recipes",
        "description": "Should fetch recipe for workflow"
    },
    {
        "query": "What does error 4004 mean?",
        "expected_source": "docs",
        "description": "Should fetch docs for error codes"
    }
]

async def test_reference_accessibility():
    """Test that reference pages are accessible"""
    
    print("=" * 80)
    print("TESTING REFERENCE DOCUMENTATION ACCESSIBILITY")
    print("=" * 80)
    
    reference_pages = [
        "post_api-hotel-search",
        "post_api-hotel-hotelid-roomsandrates-token",
        "post_api-hotel-hotelid-roomsandrates",
        "post_api-hotel-hotelid-price-recommendationid",
        "post_api-hotel-booking",
        "post_api-hotel-booking-bookingid-cancel",
        "get_api-hotel-booking-bookingid",
        "post_api-hotel-static-content",
        "get_api-hotel-autosuggest"
    ]
    
    results = {"accessible": [], "not_accessible": []}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, page in enumerate(reference_pages, 1):
            url = f"{REFERENCE_BASE}/{page}"
            print(f"\n[{i}/{len(reference_pages)}] Testing: {page}")
            
            try:
                response = await client.get(url)
                
                if response.status_code == 200:
                    content_length = len(response.text)
                    print(f"    ✓ Status: {response.status_code}")
                    print(f"    ✓ Content Length: {content_length} bytes")
                    results["accessible"].append(page)
                else:
                    print(f"    ✗ Status: {response.status_code}")
                    results["not_accessible"].append(page)
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                results["not_accessible"].append(page)
    
    print("\n" + "=" * 80)
    print(f"✓ Accessible: {len(results['accessible'])}/{len(reference_pages)}")
    print(f"✗ Not Accessible: {len(results['not_accessible'])}/{len(reference_pages)}")
    
    if results["not_accessible"]:
        print("\n❌ NOT ACCESSIBLE:")
        for page in results["not_accessible"]:
            print(f"  - {page}")
    else:
        print("\n🎉 ALL REFERENCE PAGES ARE ACCESSIBLE!")

async def test_chatbot_reference_queries():
    """Test chatbot with queries that should fetch reference docs"""
    
    print("\n" + "=" * 80)
    print("TESTING CHATBOT WITH REFERENCE QUERIES")
    print("=" * 80)
    
    # Check if chatbot is running
    try:
        async with httpx.AsyncClient() as client:
            health_response = await client.get(f"{BASE_URL}/api/health")
            if health_response.status_code != 200:
                print("\n⚠️ Chatbot is not running. Skipping chatbot tests.")
                print("   Start the server with: python -m uvicorn app.main:app --reload --port 8000")
                return
    except:
        print("\n⚠️ Chatbot is not running. Skipping chatbot tests.")
        print("   Start the server with: python -m uvicorn app.main:app --reload --port 8000")
        return
    
    print("\n✓ Chatbot is running. Testing queries...\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(TEST_QUERIES, 1):
            print(f"[TEST {i}/{len(TEST_QUERIES)}] {test_case['description']}")
            print(f"Query: {test_case['query']}")
            print("-" * 80)
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/chat",
                    json={
                        "question": test_case["query"],
                        "conversation_id": "test-reference",
                        "history": []
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✓ Status: {response.status_code}")
                    print(f"✓ Confidence: {data['confidence']}")
                    print(f"✓ Sources: {len(data['sources'])} documents")
                    
                    if data['sources']:
                        source_url = data['sources'][0]['url']
                        print(f"✓ Source URL: {source_url}")
                        
                        # Check if it fetched from expected source
                        if test_case['expected_source'] == 'reference':
                            if '/reference/' in source_url:
                                print(f"✅ CORRECT: Fetched from reference docs")
                            else:
                                print(f"⚠️ WARNING: Expected reference, got {source_url}")
                        elif test_case['expected_source'] == 'recipes':
                            if '/recipes/' in source_url:
                                print(f"✅ CORRECT: Fetched from recipes")
                            else:
                                print(f"⚠️ WARNING: Expected recipes, got {source_url}")
                        elif test_case['expected_source'] == 'docs':
                            if '/docs/' in source_url:
                                print(f"✅ CORRECT: Fetched from docs")
                            else:
                                print(f"⚠️ WARNING: Expected docs, got {source_url}")
                    
                    # Show answer preview
                    answer_preview = data['answer'][:200] + "..." if len(data['answer']) > 200 else data['answer']
                    print(f"\n📝 Answer Preview:")
                    print(f"   {answer_preview}")
                    
                else:
                    print(f"✗ Status: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"✗ Exception: {str(e)}")
            
            print()

async def test_field_detail_query():
    """Test a specific query about field details"""
    
    print("\n" + "=" * 80)
    print("DETAILED TEST: Field-Level Query")
    print("=" * 80)
    
    query = "What are all the fields in the rooms and rates request body? Explain each field."
    
    print(f"\nQuery: {query}\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={
                    "question": query,
                    "conversation_id": "test-fields",
                    "history": []
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Confidence: {data['confidence']}")
                print(f"✓ Latency: {data['latency_ms']}ms")
                
                if data['sources']:
                    print(f"\n📚 Source:")
                    print(f"   Title: {data['sources'][0]['title']}")
                    print(f"   URL: {data['sources'][0]['url']}")
                
                print(f"\n📝 FULL ANSWER:")
                print("=" * 80)
                print(data['answer'])
                print("=" * 80)
                
                # Check if answer contains field details
                answer_lower = data['answer'].lower()
                field_indicators = ['field', 'parameter', 'required', 'optional', 'type', 'string', 'integer', 'boolean']
                found_indicators = [ind for ind in field_indicators if ind in answer_lower]
                
                print(f"\n✓ Field detail indicators found: {', '.join(found_indicators)}")
                
                if len(found_indicators) >= 4:
                    print("✅ Answer appears to contain detailed field information")
                else:
                    print("⚠️ Answer may lack detailed field information")
                
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

async def main():
    """Main test runner"""
    await test_reference_accessibility()
    await test_chatbot_reference_queries()
    await test_field_detail_query()

if __name__ == "__main__":
    asyncio.run(main())
