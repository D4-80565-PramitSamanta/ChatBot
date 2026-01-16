# app/services/doc_fetcher.py
import httpx
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

class DocumentationFetcher:
    """Fetches documentation from ZentrumHub docs website"""
    
    def __init__(self):
        self.base_url = "https://docs-hotel.prod.zentrumhub.com/docs"
        self.doc_map = {
            "search": "search-api",
            "room": "roomrates-api",
            "rooms": "roomrates-api",
            "rate": "roomrates-api",
            "rates": "roomrates-api",
            "roomsandrates": "roomrates-api",
            "roomrates": "roomrates-api",
            "recommendation": "roomrates-api",
            "recommendations": "roomrates-api",
            "direct": "direct-rooms-and-rates",
            "book": "book-api",
            "booking": "book-api",
            "cancel": "cancel-api",
            "cancellation": "cancel-api",
            "static": "static-content-api",
            "content": "static-content-api",
            "hotel": "static-content-api",
            "autosuggest": "autosuggest-api",
            "suggest": "autosuggest-api",
            "location": "autosuggest-api",
            "price": "price-api",
            "pricing": "price-api"
        }
    
    async def fetch_documentation(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fetch documentation based on query keywords
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with documentation content or None
        """
        # Find relevant doc page
        query_lower = query.lower()
        doc_page = None
        
        for keyword, page in self.doc_map.items():
            if keyword in query_lower:
                doc_page = page
                break
        
        if not doc_page:
            return None
        
        try:
            url = f"{self.base_url}/{doc_page}"
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
                    "source": "live_docs"
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
