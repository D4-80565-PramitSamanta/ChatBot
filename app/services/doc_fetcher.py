# app/services/doc_fetcher.py
import httpx
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

class DocumentationFetcher:
    """Fetches documentation from ZentrumHub docs website"""
    
    def __init__(self):
        self.base_url = "https://docs-hotel.prod.zentrumhub.com/docs"
        self.recipes_url = "https://docs-hotel.prod.zentrumhub.com/recipes"
        self.reference_url = "https://docs-hotel.prod.zentrumhub.com/reference"
        
        # Enhanced keyword mapping with multiple keywords per API
        self.doc_map = {
            # Cancel API
            "cancel": "cancel-api",
            "cancellation": "cancel-api",
            "cancelled": "cancel-api",
            "cancelling": "cancel-api",
            "cancel-booking": "cancel-api",
            "cancel-reservation": "cancel-api",
            "refund": "cancel-api",
            "void": "cancel-api",
            "terminate": "cancel-api",
            
            # Rooms and Rates API
            "room": "roomrates-api",
            "rooms": "roomrates-api",
            "rate": "roomrates-api",
            "rates": "roomrates-api",
            "roomsandrates": "roomrates-api",
            "roomrates": "roomrates-api",
            "recommendation": "roomrates-api",
            "recommendations": "roomrates-api",
            "pricing": "roomrates-api",
            "availability": "roomrates-api",
            
            # Direct Rooms and Rates
            "direct": "direct-rooms-and-rates",
            "directrooms": "direct-rooms-and-rates",
            "direct-api": "direct-rooms-and-rates",
            
            # Book API
            "book": "book-api",
            "booking": "book-api",
            "reserve": "book-api",
            "reservation": "book-api",
            "confirm": "book-api",
            "confirmation": "book-api",
            
            # Search API
            "search": "search-api",
            "find": "search-api",
            "lookup": "search-api",
            "query": "search-api",
            "discover": "search-api",
            
            # Static Content API
            "static": "static-content-api",
            "content": "static-content-api",
            "hotel": "static-content-api",
            "property": "static-content-api",
            "details": "static-content-api",
            "information": "static-content-api",
            "description": "static-content-api",
            "amenities": "static-content-api",
            "facilities": "static-content-api",
            
            # Autosuggest API
            "autosuggest": "autosuggest-api",
            "suggest": "autosuggest-api",
            "suggestion": "autosuggest-api",
            "location": "autosuggest-api",
            "autocomplete": "autosuggest-api",
            "typeahead": "autosuggest-api",
            
            # Price API
            "price": "price-api",
            "pricing": "price-api",
            "quote": "price-api",
            "cost": "price-api",
            
            # Error codes (will search multiple pages)
            "error": "roomrates-api",
            "errors": "roomrates-api",
            "errorcode": "roomrates-api",
            "errorcodes": "roomrates-api"
        }
        
        # Recipes mapping for detailed guides and workflows
        self.recipes_map = {
            # Search workflows
            "search-init": "search-init",
            "searchinit": "search-init",
            "initialize": "search-init",
            "start-search": "search-init",
            "init": "search-init",
            
            "search-results": "search-results",
            "searchresults": "search-results",
            "results": "search-results",
            
            "search-polling": "search-results-polling",
            "search-results-polling": "search-results-polling",
            "polling": "search-results-polling",
            "poll": "search-results-polling",
            "async-search": "search-results-polling",
            "asynchronous": "search-results-polling",
            
            "blocking-search": "blocking-search",
            "blockingsearch": "blocking-search",
            "synchronous": "blocking-search",
            "sync-search": "blocking-search",
            "blocking": "blocking-search",
            
            # Rooms and rates workflows
            "roomsandrates": "roomsandrates",
            "rooms-rates-workflow": "roomsandrates",
            "get-rates": "roomsandrates",
            "room-rates": "roomsandrates",
            "rates": "roomsandrates",
            
            # Pricing workflows
            "pricerecommendation": "pricebyrecommendation",
            "pricebyrecommendation": "pricebyrecommendation",
            "price-recommendation": "pricebyrecommendation",
            "price-by-recommendation": "pricebyrecommendation",
            "recommendation-price": "pricebyrecommendation",
            "quote": "pricebyrecommendation",
            
            # Booking workflows
            "book-workflow": "book",
            "book": "book",
            "booking-flow": "book",
            "make-booking": "book",
            "create-reservation": "book",
            "reservation": "book",
            
            # Cancellation workflows
            "cancel-booking": "cancel-booking",
            "cancelbooking": "cancel-booking",
            "cancel-workflow": "cancel-booking",
            "cancellation-flow": "cancel-booking",
            "cancel": "cancel-booking",
            "cancellation": "cancel-booking",
            
            # Zentrum Connect specific workflows
            "zentrum-connect": "zentrum-connect-hotel-search",
            "zentrumconnect": "zentrum-connect-hotel-search",
            
            "zentrum-connect-download-content": "zentrum-connect-download-content",
            "download-content": "zentrum-connect-download-content",
            "static-content": "zentrum-connect-download-content",
            "content-download": "zentrum-connect-download-content",
            
            "zentrum-connect-hotel-search": "zentrum-connect-hotel-search",
            "connect-search": "zentrum-connect-hotel-search",
            "connect-hotel": "zentrum-connect-hotel-search",
            "connect-hotel-search": "zentrum-connect-hotel-search",
            
            "zentrum-connect-room-rates": "zentrum-connect-room-rates",
            "connect-rooms": "zentrum-connect-room-rates",
            "connect-rates": "zentrum-connect-room-rates",
            "connect-room-rates": "zentrum-connect-room-rates",
            
            "zentrum-connect-price": "zentrum-connect-price",
            "connect-price": "zentrum-connect-price",
            "smoking": "zentrum-connect-price",
            "issmoking": "zentrum-connect-price",
            "issmokinallowed": "zentrum-connect-price",
            "field": "zentrum-connect-price",
            "fields": "zentrum-connect-price",
            "parameter": "zentrum-connect-price",
            "parameters": "zentrum-connect-price",
            
            "zentrum-connect-book": "zentrum-connect-book",
            "connect-book": "zentrum-connect-book",
            "connect-booking": "zentrum-connect-book",
            
            "zentrum-connect-retreive-booking": "zentrum-connect-retreive-booking",
            "zentrum-connect-retrieve-booking": "zentrum-connect-retreive-booking",
            "retrieve-booking": "zentrum-connect-retreive-booking",
            "retreive-booking": "zentrum-connect-retreive-booking",
            "get-booking": "zentrum-connect-retreive-booking",
            "fetch-booking": "zentrum-connect-retreive-booking",
            "connect-retrieve": "zentrum-connect-retreive-booking",
            
            "zentrum-connect-rate-combinability": "zentrum-connect-rate-combinability",
            "rate-combinability": "zentrum-connect-rate-combinability",
            "combinability": "zentrum-connect-rate-combinability",
            "combine-rates": "zentrum-connect-rate-combinability",
            "ratecombinability": "zentrum-connect-rate-combinability",
            "connect-combinability": "zentrum-connect-rate-combinability"
        }
        
        # Reference API mapping for detailed field specifications
        self.reference_map = {
            # Search API
            "search": "post_api-hotel-search",
            "hotel-search": "post_api-hotel-search",
            "search-hotels": "post_api-hotel-search",
            "find-hotels": "post_api-hotel-search",
            
            # Rooms and Rates API
            "roomsandrates": "post_api-hotel-hotelid-roomsandrates-token",
            "rooms-rates": "post_api-hotel-hotelid-roomsandrates-token",
            "get-rooms": "post_api-hotel-hotelid-roomsandrates-token",
            "room-availability": "post_api-hotel-hotelid-roomsandrates-token",
            "request-body": "post_api-hotel-hotelid-roomsandrates-token",
            "request-fields": "post_api-hotel-hotelid-roomsandrates-token",
            "request-schema": "post_api-hotel-hotelid-roomsandrates-token",
            "request-parameters": "post_api-hotel-hotelid-roomsandrates-token",
            "request-format": "post_api-hotel-hotelid-roomsandrates-token",
            "how-to-request": "post_api-hotel-hotelid-roomsandrates-token",
            "api-request": "post_api-hotel-hotelid-roomsandrates-token",
            
            # Direct Rooms and Rates
            "direct-rooms": "post_api-hotel-hotelid-roomsandrates",
            "direct-rates": "post_api-hotel-hotelid-roomsandrates",
            
            # Price by Recommendation
            "price-recommendation": "post_api-hotel-hotelid-price-recommendationid",
            "get-price": "post_api-hotel-hotelid-price-recommendationid",
            "quote-price": "post_api-hotel-hotelid-price-recommendationid",
            
            # Book API
            "book": "post_api-hotel-booking",
            "booking": "post_api-hotel-booking",
            "create-booking": "post_api-hotel-booking",
            "make-reservation": "post_api-hotel-booking",
            
            # Cancel API
            "cancel": "post_api-hotel-booking-bookingid-cancel",
            "cancel-booking": "post_api-hotel-booking-bookingid-cancel",
            "cancellation": "post_api-hotel-booking-bookingid-cancel",
            
            # Get Booking
            "get-booking": "get_api-hotel-booking-bookingid",
            "retrieve-booking": "get_api-hotel-booking-bookingid",
            "fetch-booking": "get_api-hotel-booking-bookingid",
            
            # Static Content
            "static-content": "post_api-hotel-static-content",
            "hotel-content": "post_api-hotel-static-content",
            "hotel-details": "post_api-hotel-static-content",
            "property-info": "post_api-hotel-static-content",
            
            # Autosuggest
            "autosuggest": "get_api-hotel-autosuggest",
            "location-suggest": "get_api-hotel-autosuggest",
            "autocomplete": "get_api-hotel-autosuggest"
        }
    
    async def fetch_documentation(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fetch documentation based on query keywords with improved scoring
        Now searches 3 sources: /reference/ (API specs), /docs/ (guides), /recipes/ (workflows)
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with documentation content or None
        """
        # Find relevant doc page with scoring
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Extract error code if present (e.g., "401", "4004", "5000")
        error_code = None
        for word in query_words:
            if word.isdigit() and len(word) in [3, 4]:
                error_code = word
                break
        
        # If error code detected, search all API pages for error codes
        if error_code or 'error' in query_lower:
            print(f"🔍 Detected error query, searching all API pages for error codes")
            # Try multiple API pages that typically have error codes
            error_pages = [
                "roomrates-api",
                "book-api", 
                "cancel-api",
                "search-api",
                "static-content-api",
                "direct-rooms-and-rates"
            ]
            
            # Fetch all error pages and combine
            all_content = []
            for page in error_pages:
                try:
                    url = f"{self.base_url}/{page}"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=10.0)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            content = soup.get_text(separator='\n', strip=True)
                            
                            # Check if this page has error codes
                            if 'error' in content.lower() and ('code' in content.lower() or error_code in content):
                                all_content.append({
                                    "page": page,
                                    "url": url,
                                    "content": content
                                })
                                print(f"  ✓ Found error codes in {page}")
                except:
                    continue
            
            if all_content:
                # Combine all error documentation
                combined_content = "\n\n=== ERROR CODES FROM MULTIPLE APIs ===\n\n"
                urls = []
                for doc in all_content:
                    combined_content += f"\n--- {doc['page']} ---\n{doc['content']}\n"
                    urls.append(doc['url'])
                
                return {
                    "title": "ZentrumHub API Error Codes",
                    "url": urls[0] if urls else f"{self.base_url}/roomrates-api",
                    "content": combined_content,
                    "source": "live_docs",
                    "score": 100
                }
        
        # Regular keyword matching for non-error queries
        doc_scores = {}
        recipe_scores = {}
        reference_scores = {}
        
        # Score docs pages
        for keyword, page in self.doc_map.items():
            score = 0
            if keyword in query_lower:
                score += 20
                # Boost score for exact phrase matches
                if keyword == "cancel-booking" and "cancel" in query_lower and "booking" in query_lower:
                    score += 50  # High boost for cancel booking queries
            for word in query_words:
                if keyword in word or word in keyword:
                    score += 10
            if any(keyword in word for word in query_words):
                score += 5
            
            # Special boost for cancel-related queries
            if page == "cancel-api" and any(term in query_lower for term in ['cancel', 'cancellation', 'refund']):
                score += 30
                
            if score > 0:
                doc_scores[page] = doc_scores.get(page, 0) + score
        
        # Score recipes pages
        for keyword, page in self.recipes_map.items():
            score = 0
            if keyword in query_lower:
                score += 20
                # Boost score for exact phrase matches
                if keyword == "cancel-booking" and "cancel" in query_lower and "booking" in query_lower:
                    score += 50  # High boost for cancel booking queries
            for word in query_words:
                if keyword in word or word in keyword:
                    score += 10
            if any(keyword in word for word in query_words):
                score += 5
                
            # Special boost for cancel-related queries in recipes
            if page == "cancel-booking" and any(term in query_lower for term in ['cancel', 'cancellation', 'refund']):
                score += 30
                
            if score > 0:
                recipe_scores[page] = recipe_scores.get(page, 0) + score
        
        # Score reference pages (HIGHEST PRIORITY for field/request details)
        for keyword, page in self.reference_map.items():
            score = 0
            if keyword in query_lower:
                score += 30  # Higher base score for reference
            for word in query_words:
                if keyword in word or word in keyword:
                    score += 15  # Higher word match score
            if any(keyword in word for word in query_words):
                score += 8
            # Boost score for field/request/schema related queries
            if any(term in query_lower for term in ['field', 'request', 'body', 'parameter', 'schema', 'format', 'how to', 'create', 'send']):
                score += 25
            if score > 0:
                reference_scores[page] = reference_scores.get(page, 0) + score
        
        # Determine best match (reference > recipes > docs)
        best_doc_score = max(doc_scores.values()) if doc_scores else 0
        best_recipe_score = max(recipe_scores.values()) if recipe_scores else 0
        best_reference_score = max(reference_scores.values()) if reference_scores else 0
        
        # Choose the highest scoring source
        if best_reference_score > 0 and best_reference_score >= best_recipe_score and best_reference_score >= best_doc_score:
            # Fetch from reference (API specifications)
            doc_page = max(reference_scores.items(), key=lambda x: x[1])[0]
            url = f"{self.reference_url}/{doc_page}"
            source_type = "reference"
            score = best_reference_score
        elif best_recipe_score > best_doc_score:
            # Fetch from recipes
            doc_page = max(recipe_scores.items(), key=lambda x: x[1])[0]
            url = f"{self.recipes_url}/{doc_page}"
            source_type = "recipes"
            score = best_recipe_score
        elif best_doc_score > 0:
            # Fetch from docs
            doc_page = max(doc_scores.items(), key=lambda x: x[1])[0]
            url = f"{self.base_url}/{doc_page}"
            source_type = "docs"
            score = best_doc_score
        else:
            return None
        
        try:
            print(f"📄 Fetching from {source_type}: {url} (score: {score})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                content = soup.get_text(separator='\n', strip=True)
                
                return {
                    "title": doc_page.replace('-', ' ').replace('_', ' ').title(),
                    "url": url,
                    "content": content,
                    "source": f"live_{source_type}",
                    "score": score
                }
        except Exception as e:
            print(f"Error fetching documentation: {e}")
            return None
    
    def save_to_knowledge_base(self, doc_data: Dict[str, Any], filename: str = "knowledge-base-dynamic.json"):
        """
        Save fetched documentation to knowledge base
        
        Args:
            doc_data: Documentation data to save
            filename: Knowledge base file name
        """
        try:
            # Load existing knowledge base
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
            except FileNotFoundError:
                kb = {}
            
            # Add new documentation
            key = doc_data['title'].lower().replace(' ', '_')
            kb[key] = {
                "title": doc_data['title'],
                "url": doc_data['url'],
                "content": doc_data['content'],
                "source": "auto_fetched",
                "last_updated": "auto"
            }
            
            # Save updated knowledge base
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved {doc_data['title']} to knowledge base")
            return True
        except Exception as e:
            print(f"✗ Error saving to knowledge base: {e}")
            return False
