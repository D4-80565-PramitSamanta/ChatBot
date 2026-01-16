# app/controllers/chat_controller.py
from fastapi import APIRouter, HTTPException
from typing import List
import time

from app.models.schemas import ChatRequest, ChatResponse, Source
from app.services.rag_service import RAGService
from app.utils.analytics import analytics

router = APIRouter(prefix="/api", tags=["chat"])

# RAG service will be injected
rag_service: RAGService = None

def set_rag_service(service: RAGService):
    """Set the RAG service instance"""
    global rag_service
    rag_service = service

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "zentrumhub-chatbot",
        "version": "1.0.0",
        "llm": "gemini-2.5-pro"
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Layer 1 (Controller): Receives request, measures latency, returns response
    """
    start_time = time.time()
    
    try:
        # Call RAG service (Layer 2)
        result = await rag_service.generate_answer(request.question)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        client_id = request.conversation_id or "unknown"
        analytics.log_query(request.question, result["confidence"], client_id)
        
        # Build sources with proper format
        sources = []
        for source_meta in result.get("sources", []):
            # Get URL from metadata
            url = source_meta.get("url", "https://docs-hotel.prod.zentrumhub.com")
            source_type = source_meta.get("source", "documentation")
            title = source_meta.get("key", source_meta.get("title", "ZentrumHub API Documentation"))
            
            # Extract snippet from answer (first 150 chars)
            snippet = result["answer"][:150] + "..." if len(result["answer"]) > 150 else result["answer"]
            
            sources.append(Source(
                title=title,
                section=source_type,
                url=url,
                snippet=snippet
            ))
        
        # If no sources, add default
        if not sources and result.get("source_type") == "live_documentation":
            sources.append(Source(
                title="ZentrumHub Hotel API Documentation",
                section="live_docs",
                url="https://docs-hotel.prod.zentrumhub.com/docs",
                snippet=result["answer"][:150] + "..." if len(result["answer"]) > 150 else result["answer"]
            ))
        
        # Return response
        return ChatResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=sources,
            tokens_used=None,
            latency_ms=latency_ms,
            service_used="gemini_2.5_pro"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.get("/suggested-questions")
async def suggested_questions():
    """Get suggested questions"""
    return {
        "questions": [
            "How do I search for hotels?",
            "How to authenticate API requests?",
            "What does error 429 mean?",
            "Show booking API example",
            "How to cancel a reservation?",
            "What are the rate limits?"
        ]
    }

@router.get("/analytics/top-queries")
async def top_queries(limit: int = 10):
    """Get top queries analytics"""
    return {
        "total_queries": analytics.get_total_queries(),
        "top_queries": analytics.get_top_queries(limit)
    }

@router.get("/analytics/unanswered-questions")
async def unanswered_questions(limit: int = 20):
    """Get unanswered questions"""
    return {
        "total_unanswered": sum(
            q["count"] for q in analytics.get_unanswered_questions(limit)
        ),
        "questions": analytics.get_unanswered_questions(limit)
    }
