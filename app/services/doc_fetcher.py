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
        
        # Enhanced keyword mapping with multiple keywords per API
        self.doc_map = {
            # Cancel API
            "cancel": "cancel-api",
            "cancellation": "cancel-api",
            "cancelled": "cancel-api",
            "cancelling": "cancel-api",
            
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
            
            # Direct Rooms and Rates
            "direct": "direct-rooms-and-rates",
            "directrooms": "direct-rooms-and-rates",
            
            # Book API
            "book": "book-api",
            "booking": "book-api",
            "reserve": "book-api",
            "reservation": "book-api",
            
            # Search API
            "search": "search-api",
            "find": "search-api",
            "lookup": "search-api",
            
            # Static Content API
            "static": "static-content-api",
            "content": "static-content-api",
            "hotel": "static-content-api",
            "property": "static-content-api",
            "details": "static-content-api",
            
            # Autosuggest API
            "autosuggest": "autosuggest-api",
            "suggest": "autosuggest-api",
            "suggestion": "autosuggest-api",
            "location": "autosuggest-api",
            
            # Price API
            "price": "price-api",
            "pricing": "price-api",
            "quote": "price-api"
        }
        
        # Recipes mapping for detailed guides
        self.recipes_map = {
            "price": "zentrum-connect-price",
            "pricing": "zentrum-connect-price",
            "smoking": "zentrum-connect-price",
            "issmoking": "zentrum-connect-price",
            "issmokinallowed": "zentrum-connect-price",
            "field": "zentrum-connect-price",
            "fields": "zentrum-connect-price",
            "parameter": "zentrum-connect-price",
            "parameters": "zentrum-connect-price"
        }
    
    async def fetch_documentation(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fetch documentation based on query keywords with improved scoring
        
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
        
        # Score docs pages
        for keyword, page in self.doc_map.items():
            score = 0
            if keyword in query_lower:
                score += 20
            for word in query_words:
                if keyword in word or word in keyword:
                    score += 10
            if any(keyword in word for word in query_words):
                score += 5
            if score > 0:
                doc_scores[page] = doc_scores.get(page, 0) + score
        
        # Score recipes pages
        for keyword, page in self.recipes_map.items():
            score = 0
            if keyword in query_lower:
                score += 20
            for word in query_words:
                if keyword in word or word in keyword:
                    score += 10
            if any(keyword in word for word in query_words):
                score += 5
            if score > 0:
                recipe_scores[page] = recipe_scores.get(page, 0) + score
        
        # Determine best match (docs or recipes)
        best_doc_score = max(doc_scores.values()) if doc_scores else 0
        best_recipe_score = max(recipe_scores.values()) if recipe_scores else 0
        
        if best_recipe_score > best_doc_score:
            # Fetch from recipes
            doc_page = max(recipe_scores.items(), key=lambda x: x[1])[0]
            url = f"{self.recipes_url}/{doc_page}"
            is_recipe = True
        elif best_doc_score > 0:
            # Fetch from docs
            doc_page = max(doc_scores.items(), key=lambda x: x[1])[0]
            url = f"{self.base_url}/{doc_page}"
            is_recipe = False
        else:
            return None
        
        try:
            print(f"📄 Fetching: {url} (score: {max(best_doc_score, best_recipe_score)})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                content = soup.get_text(separator='\n', strip=True)
                
                return {
                    "title": doc_page.replace('-', ' ').title(),
                    "url": url,
                    "content": content,
                    "source": "live_recipes" if is_recipe else "live_docs",
                    "score": max(best_doc_score, best_recipe_score)
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
