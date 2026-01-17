# app/services/rag_service.py
import json
from typing import List, Dict, Any
from app.config import config
from app.llm.llm_client import LLMClient
from app.services.doc_fetcher import DocumentationFetcher
from app.services.cache_service import CacheService


class RAGService:
    """RAG Service - Hybrid mode with caching"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.doc_fetcher = DocumentationFetcher()
        self.cache_service = CacheService()
        print("✓ RAG Service initialized - HYBRID mode with caching enabled")
    
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
    
    def _search_local_knowledge_base(self, question: str) -> List[Dict[str, Any]]:
        """
        Search local knowledge base files with improved scoring
        
        NEW SCORING SYSTEM:
        - 2 points per word match (was 1)
        - 20 points for exact phrase match (was 10)  
        - 15 points if document KEY matches query (e.g., "cancel_api")
        - 10 points if document TITLE matches query
        """
        question_lower = question.lower()
        question_words = question_lower.split()
        
        results = []
        
        # Knowledge base files to search - SEARCH ALL FILES
        kb_files = [
            'knowledge-base.json',
            'knowledge-base-extended.json',
            'knowledge-base-dynamic.json',
            'knowledge-base-rooms-rates.json',
            'data/knowledge-base.json',
            'data/knowledge-base-extended.json',
            'data/complete-documentation.json'
        ]
        
        for kb_file in kb_files:
            try:
                print(f"🔍 Searching in {kb_file}")
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                    print(f"✓ Loaded {len(kb_data)} entries from {kb_file}")
                    
                    # Handle different file structures
                    if kb_file == 'data/complete-documentation.json':
                        # Complete documentation has nested structure
                        if 'documentation' in kb_data:
                            kb_data = kb_data['documentation']
                    
                    for key, value in kb_data.items():
                        if not isinstance(value, dict):
                            continue
                            
                        title = value.get('title', key)
                        description = value.get('description', '')
                        content = json.dumps(value, indent=2)
                        
                        # Normalize text for searching
                        key_normalized = key.lower().replace('_', ' ').replace('-', ' ')
                        title_normalized = title.lower()
                        
                        # Calculate score with COMPREHENSIVE SEARCH
                        score = 0
                        
                        # Search in ALL content, not just keys and titles
                        search_text = f"{key_normalized} {title_normalized} {description.lower()} {content.lower()}"
                        
                        # 15 points if document KEY matches query (e.g., "cancel_api")
                        if any(word in key_normalized for word in question_words):
                            score += 15
                            
                        # 10 points if document TITLE matches query
                        if any(word in title_normalized for word in question_words):
                            score += 10
                            
                        # 2 points per word match in any field
                        for word in question_words:
                            if word in search_text:
                                score += 2
                                
                        # 20 points for exact phrase match anywhere in content
                        if question_lower in search_text:
                            score += 20
                            
                        # PRIORITY OVERRIDE: For field queries, heavily prioritize api_field_definitions
                        if any(field_term in question_lower for field_term in ['what is', 'commission', 'taxes', 'publishedrate', 'baserate', 'totalrate', 'isincludedinbaserate']):
                            if key == 'api_field_definitions':
                                score += 1000  # Massive boost to ensure this wins
                            elif 'field' in key_normalized or 'definition' in key_normalized:
                                score += 500  # High boost for other field-related docs
                        
                        # PRIORITY OVERRIDE: For workflow/API queries, prioritize workflow documents
                        if any(workflow_term in question_lower for workflow_term in ['blocking search', 'async search', 'search workflow', 'polling', 'search init']):
                            if any(workflow_key in key_normalized for workflow_key in ['blocking_search', 'async_search', 'search_workflow', 'polling', 'search_init']):
                                score += 1000  # Massive boost for workflow documents
                            
                        # Special boost for cancel-related queries
                        if 'cancel' in question_lower and 'cancel' in search_text:
                            score += 25
                            
                        if score > 0:
                            results.append({
                                'key': key,
                                'title': title,
                                'content': content,
                                'score': score,
                                'file': kb_file
                            })
                            
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"✗ Error loading {kb_file}: {e}")
                continue
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if results:
            print(f"📚 Local KB search results:")
            for i, result in enumerate(results[:5]):  # Show top 5 results
                print(f"  {i+1}. {result['key']} (score: {result['score']}) from {result['file']}")
        else:
            print(f"📚 No local KB results found for: {question}")
        
        return results
    
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
     * Required Parameters (with data types and descriptions)
     * Optional Parameters (with data types and descriptions)
     * Request Body Fields (if applicable, with complete field details)
     * Response Details (structure and fields)
     * Error Codes (if applicable)
   - Include practical examples or use cases when available

3. FIELD-LEVEL DETAILS (CRITICAL):
   - When the documentation includes API reference specifications, provide COMPLETE field details:
     * Field name
     * Data type (string, integer, boolean, array, object)
     * Required or optional
     * Description and purpose
     * Valid values or constraints
     * Example values
   - For request bodies, show the complete JSON structure with all fields
   - Explain nested objects and arrays clearly

4. FORMATTING REQUIREMENTS:
   - Use **bold** for API names, important terms, and field names
   - Use `code blocks` for:
     * Endpoints: `POST /api/v1/hotels/{{hotel_id}}/rooms`
     * Parameters: `searchResponseToken`, `hotel_id`
     * Field names: `rateCombinabilityType`, `allGuestInfoRequired`
     * JSON structures and examples
   - Use bullet points (•) for lists
   - Use numbered lists for sequential steps
   - Use > blockquotes for important notes or warnings

5. REQUEST/RESPONSE EXAMPLES:
   - When available, include complete request body examples
   - Show response structure with field descriptions
   - Explain what each field means and when to use it
   - Include data type information for all fields

6. SPECIFIC GUIDELINES:
   - For "rooms and rates" queries: Focus on Get Rooms and Rates API or Direct Rooms and Rates API
   - For "booking" queries: Focus on Book API details with complete request body
   - For "cancel" queries: Focus on Cancel API details
   - For "search" queries: Focus on Search API details
   - For "hotel content" or "static content" queries: Focus on Static Content API
   - For "field" or "parameter" queries: Provide detailed field specifications from reference docs
   - Always include error codes when discussing APIs

7. EXAMPLES & USE CASES:
   - When available, include practical examples from the documentation
   - Explain when to use one API vs another (e.g., Direct Rooms vs Get Rooms)
   - Mention related APIs that might be useful
   - Show complete request/response cycles

8. TONE & STYLE:
   - Be professional but conversational
   - Use clear, simple language
   - Avoid jargon unless it's from the API documentation
   - Be helpful and anticipate follow-up questions

9. QUALITY CHECKS:
   - Ensure all endpoints are complete and accurate
   - Verify HTTP methods are correct
   - Double-check parameter names match the documentation
   - Confirm error codes are accurate
   - Validate field names and data types

ANSWER (provide your response below):"""
        
        return prompt
    
    def build_explain_prompt(self, error_content: str, context_docs: List[Dict[str, Any]]) -> str:
        """Build specialized prompt for error code explanations"""
        context = "\n\n---\n\n".join([
            f"[Document {i + 1}]\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""You are a ZentrumHub Hotel API error diagnostic expert. Your role is to explain error codes and provide actionable solutions.

CONTEXT - RELEVANT DOCUMENTATION:
{context}

ERROR TO EXPLAIN: {error_content}

CRITICAL INSTRUCTIONS FOR ERROR EXPLANATION:

1. IDENTIFY THE ERROR CODE:
   - Extract the error code number (e.g., 4001, 4004, 5000)
   - Look for the error code in the "Error Codes" section of the documentation
   - Match the exact error code and message

2. PROVIDE STRUCTURED EXPLANATION:
   
   **Summary** (1-2 sentences):
   - What does this error mean?
   - When does it occur?
   
   **Details** (3-5 bullet points):
   - Root cause of the error
   - Common scenarios that trigger this error
   - What went wrong in the API request/response
   - Impact on the booking flow
   - Related error codes if any
   
   **Recommended Actions** (3-5 specific steps):
   - Immediate actions to resolve the error
   - How to prevent this error in future
   - What to check in the request
   - When to contact support
   - Include correlationId usage if mentioned

3. ERROR CODE SPECIFIC GUIDANCE:
   - **4001**: Focus on request validation, check fields[] array
   - **4004**: Explain sold out scenario, suggest alternative dates/hotels
   - **4005**: Price changed, explain re-search requirement
   - **4006**: Rate expired, explain token expiration
   - **4007**: Duplicate booking, explain idempotency
   - **5000-5004**: System/supplier errors, emphasize support contact with correlationId

4. FORMATTING:
   - Use **bold** for error codes and important terms
   - Use `code` for field names and parameters
   - Use bullet points for lists
   - Be concise but comprehensive

5. ALWAYS INCLUDE:
   - The exact error code and message from documentation
   - Whether this is a client error (4xxx) or server error (5xxx)
   - If correlationId should be provided to support

PROVIDE YOUR ERROR EXPLANATION:"""
        
        return prompt
    
    def _is_not_found_response(self, answer: str) -> bool:
        """
        Check if the answer indicates information was not found
        
        Returns True if the answer contains phrases indicating missing information
        """
        not_found_phrases = [
            "not available in the current documentation",
            "not mentioned",
            "not defined",
            "not found",
            "information is not available",
            "does not contain",
            "is not provided",
            "not detailed",
            "not specified",
            "not included in the documentation"
        ]
        
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in not_found_phrases)
    
    async def generate_answer(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG pipeline - HYBRID mode with caching
        
        Flow:
        1. Check response cache first
        2. Check local knowledge base files with improved scoring
        3. If no good match, fetch from live documentation (with doc caching)
        4. Generate answer and cache it
        5. Return cached or fresh response
        """
        # Check response cache first
        cached_response = self.cache_service.get_response(question, "question")
        if cached_response:
            return cached_response
        
        print(f"🔍 Searching for: {question}")
        
        # First, search local knowledge base files with improved scoring
        local_docs = self._search_local_knowledge_base(question)
        
        # ALWAYS use local knowledge base if ANY results found, ignore scoring threshold
        if local_docs:
            print(f"✓ Found in local knowledge base: {local_docs[0]['title']} (score: {local_docs[0]['score']})")
            
            # Use ALL top results for better context, not just the first one
            context_docs = []
            for i, doc in enumerate(local_docs[:3]):  # Use top 3 results
                context_docs.append({
                    "text": f"{doc['title']}\n{doc['content']}",
                    "metadata": {
                        "source": "local_knowledge_base",
                        "file": doc['file'],
                        "title": doc['title'],
                        "key": doc['key']
                    }
                })
            
            source_type = "local_knowledge_base"
        else:
            # Fallback to live documentation
            print(f"📚 No good local match, fetching live documentation")
            
            # Check documentation cache
            cached_doc = self.cache_service.get_documentation(question)
            if cached_doc:
                live_doc = cached_doc
            else:
                # Fetch from live documentation
                live_doc = await self.doc_fetcher.fetch_documentation(question)
                if live_doc:
                    # Cache the documentation
                    self.cache_service.set_documentation(question, live_doc)
            
            if not live_doc:
                response = {
                    "answer": "I couldn't find relevant documentation. Please ensure the question is about ZentrumHub Hotel API or visit https://docs-hotel.prod.zentrumhub.com/docs directly.",
                    "confidence": "low",
                    "sources": [],
                    "relevant_docs": 0,
                    "source_type": "none"
                }
                return response
            
            print(f"✓ Using live documentation: {live_doc['title']} from {live_doc['url']}")
            
            # Use documentation as context
            context_docs = [{
                "text": f"{live_doc['title']}\n{live_doc['content']}",
                "metadata": {
                    "source": "live_docs",
                    "url": live_doc['url'],
                    "title": live_doc['title']
                }
            }]
            
            source_type = "live_documentation"
        
        # Build prompt with context
        prompt = self.build_prompt(question, context_docs)
        
        # Generate answer using Gemini 2.5 Pro
        answer = await self.llm_client.generate(prompt)
        
        # Check if this is a "not found" response - don't cache these
        if self._is_not_found_response(answer):
            print(f"⚠️ Not caching 'not found' response for: {question}")
            return {
                "answer": answer,
                "confidence": "low",  # Set confidence to low for not found responses
                "sources": [doc.get("metadata", {}) for doc in context_docs],
                "relevant_docs": len(context_docs),
                "source_type": source_type
            }
        
        # Prepare response
        response = {
            "answer": answer,
            "confidence": "high",
            "sources": [doc.get("metadata", {}) for doc in context_docs],
            "relevant_docs": len(context_docs),
            "source_type": source_type
        }
        
        # Cache the response (only if it's not a "not found" response)
        self.cache_service.set_response(question, response, "question")
        
        return response
    
    async def explain_error(self, error_content: str) -> Dict[str, Any]:
        """
        Explain error codes using live documentation
        
        Args:
            error_content: Error message or code to explain
            
        Returns:
            Dictionary with explanation and metadata
        """
        # Fetch documentation about errors
        print(f"🔍 Fetching error documentation for: {error_content}")
        live_doc = await self.doc_fetcher.fetch_documentation(f"error {error_content}")
        
        if not live_doc:
            return {
                "answer": "Error code not found in documentation. Please check the error code or visit https://docs-hotel.prod.zentrumhub.com/docs",
                "confidence": "low",
                "sources": [],
                "relevant_docs": 0,
                "source_type": "none"
            }
        
        print(f"✓ Fetched error documentation from {live_doc['url']}")
        
        # Use live documentation as context
        context_docs = [{
            "text": f"{live_doc['title']}\n{live_doc['content']}",
            "metadata": {
                "source": "live_docs",
                "url": live_doc['url'],
                "title": live_doc['title']
            }
        }]
        
        # Build specialized error explanation prompt
        prompt = self.build_explain_prompt(error_content, context_docs)
        
        # Generate explanation using Gemini 2.5 Pro
        answer = await self.llm_client.generate(prompt)
        
        # Check if this is a "not found" response - don't cache these
        if self._is_not_found_response(answer):
            print(f"⚠️ Not caching 'not found' error explanation for: {error_content}")
            return {
                "answer": answer,
                "confidence": "low",  # Set confidence to low for not found responses
                "sources": [doc.get("metadata", {}) for doc in context_docs],
                "relevant_docs": len(context_docs),
                "source_type": "live_documentation"
            }
        
        # Return response (only cache if it's not a "not found" response)
        return {
            "answer": answer,
            "confidence": "high",
            "sources": [doc.get("metadata", {}) for doc in context_docs],
            "relevant_docs": len(context_docs),
            "source_type": "live_documentation"
        }
