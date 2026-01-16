# app/services/rag_service.py
import json
from typing import List, Dict, Any
from app.config import config
from app.llm.llm_client import LLMClient
from app.services.doc_fetcher import DocumentationFetcher


class RAGService:
    """RAG Service - Always fetches from live documentation"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.doc_fetcher = DocumentationFetcher()
        print("✓ RAG Service initialized - Using LIVE documentation only (no static knowledge base)")
    
    def _load_documents(self):
        """Load documents from JSON files into vector store"""
        try:
            # Load main knowledge base
            with open(config.KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
                kb = json.load(f)
                for key, value in kb.items():
                    if isinstance(value, dict):
                        title = value.get('title', key)
                        text = f"{title}\n{json.dumps(value, indent=2)}"
                        self.vector_store.add_document(text, {
                            "source": "knowledge_base",
                            "key": key,
                            "title": title
                        })
                    else:
                        text = f"{key}\n{json.dumps(value, indent=2)}"
                        self.vector_store.add_document(text, {
                            "source": "knowledge_base",
                            "key": key,
                            "title": key
                        })
            
            # Load rooms and rates documentation
            try:
                with open('knowledge-base-rooms-rates.json', 'r', encoding='utf-8') as f:
                    rooms_kb = json.load(f)
                    for key, value in rooms_kb.items():
                        if isinstance(value, dict):
                            title = value.get('title', key)
                            text = f"{title}\n{json.dumps(value, indent=2)}"
                            self.vector_store.add_document(text, {
                                "source": "rooms_rates_kb",
                                "key": key,
                                "title": title
                            })
                        else:
                            text = f"{key}\n{json.dumps(value, indent=2)}"
                            self.vector_store.add_document(text, {
                                "source": "rooms_rates_kb",
                                "key": key,
                                "title": key
                            })
            except FileNotFoundError:
                pass
            
            print(f"✓ Loaded {len(self.vector_store.documents)} documents")
        except Exception as e:
            print(f"✗ Error loading documents: {e}")
    
    def retrieve_context(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the question"""
        return self.vector_store.search(question, config.TOP_K_DOCUMENTS)
    
    def build_prompt(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Build enhanced prompt for LLM with retrieved context"""
        context = "\n\n---\n\n".join([
            f"[Document {i + 1}]\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""You are a ZentrumHub Hotel API expert assistant. Your role is to provide accurate, detailed, and actionable answers about the ZentrumHub Hotel API based on the official documentation.

CONTEXT - RELEVANT DOCUMENTATION:
{context}

USER QUESTION: {question}

CRITICAL INSTRUCTIONS:

1. ACCURACY & COMPLETENESS:
   - Answer ONLY using information from the documentation above
   - If information is not in the documentation, clearly state: "This information is not available in the current documentation"
   - Never make assumptions or provide information not explicitly stated in the docs

2. STRUCTURE YOUR ANSWER:
   - Start with a clear, direct answer to the question
   - Provide complete API details in this order:
     * API Name and Purpose
     * HTTP Method (GET, POST, etc.)
     * Full Endpoint URL with placeholders
     * Required Parameters
     * Optional Parameters (if any)
     * Response Details
     * Error Codes (if applicable)
   - Include practical examples or use cases when available

3. FORMATTING REQUIREMENTS:
   - Use **bold** for API names, important terms, and field names
   - Use `code blocks` for:
     * Endpoints: `GET /api/v1/hotels/{{hotel_id}}/rooms`
     * Parameters: `searchResponseToken`, `hotel_id`
     * Field names: `rateCombinabilityType`, `allGuestInfoRequired`
   - Use bullet points (•) for lists
   - Use numbered lists for sequential steps
   - Use > blockquotes for important notes or warnings

4. SPECIFIC GUIDELINES:
   - For "rooms and rates" queries: Focus on Get Rooms and Rates API or Direct Rooms and Rates API
   - For "booking" queries: Focus on Book API details
   - For "cancel" queries: Focus on Cancel API details
   - For "search" queries: Focus on Search API details
   - For "hotel content" or "static content" queries: Focus on Static Content API
   - Always include error codes when discussing APIs

5. EXAMPLES & USE CASES:
   - When available, include practical examples from the documentation
   - Explain when to use one API vs another (e.g., Direct Rooms vs Get Rooms)
   - Mention related APIs that might be useful

6. TONE & STYLE:
   - Be professional but conversational
   - Use clear, simple language
   - Avoid jargon unless it's from the API documentation
   - Be helpful and anticipate follow-up questions

7. QUALITY CHECKS:
   - Ensure all endpoints are complete and accurate
   - Verify HTTP methods are correct
   - Double-check parameter names match the documentation
   - Confirm error codes are accurate

ANSWER (provide your response below):"""
        
        return prompt
    
    async def generate_answer(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG pipeline - ALWAYS uses live documentation
        
        Flow:
        1. Fetch from live documentation (https://docs-hotel.prod.zentrumhub.com/docs)
        2. Generate answer from fresh content
        3. No static knowledge base - always current
        """
        # ALWAYS fetch from live documentation
        print(f"🔍 Fetching LIVE documentation for: {question}")
        live_doc = await self.doc_fetcher.fetch_documentation(question)
        
        if not live_doc:
            return {
                "answer": "I couldn't fetch the latest documentation. Please ensure the question is about ZentrumHub Hotel API or visit https://docs-hotel.prod.zentrumhub.com/docs directly.",
                "confidence": "low",
                "sources": [],
                "relevant_docs": 0,
                "source_type": "none"
            }
        
        print(f"✓ Fetched live documentation: {live_doc['title']} from {live_doc['url']}")
        
        # Use live documentation as context
        context_docs = [{
            "text": f"{live_doc['title']}\n{live_doc['content']}",
            "metadata": {
                "source": "live_docs",
                "url": live_doc['url'],
                "title": live_doc['title']
            }
        }]
        
        # Build prompt with live context
        prompt = self.build_prompt(question, context_docs)
        
        # Generate answer using Gemini 2.5 Pro
        answer = await self.llm_client.generate(prompt)
        
        # Return response with live documentation source
        return {
            "answer": answer,
            "confidence": "high",
            "sources": [doc.get("metadata", {}) for doc in context_docs],
            "relevant_docs": len(context_docs),
            "source_type": "live_documentation"
        }
