# app/controllers/chat_controller.py
from fastapi import APIRouter, HTTPException
from typing import List
import time

from app.models.schemas import ChatRequest, ChatResponse, Source, ExplainRequest, ExplainResponse, FeedbackRequest, FeedbackResponse
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

@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
    """
    Explain error codes and API issues
    
    Analyzes error messages and provides detailed explanations with recommended actions
    """
    start_time = time.time()
    
    try:
        # Use specialized error explanation method
        result = await rag_service.explain_error(request.content)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        client_id = request.client_id or "unknown"
        analytics.log_query(f"[EXPLAIN] {request.content}", result["confidence"], client_id)
        
        # Parse the structured answer with improved logic
        answer = result["answer"]
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        
        # Extract summary - look for first substantial paragraph
        summary = ""
        for line in lines:
            # Skip markdown headers and empty lines
            if line.startswith('#') or line.startswith('**') or line.startswith('*'):
                continue
            if len(line) > 20 and not line.startswith('-') and not line.startswith('•'):
                summary = line.replace('**', '').replace('*', '')
                break
        
        if not summary:
            summary = lines[0].replace('**', '').replace('*', '') if lines else "Error explanation"
        
        # Extract details - look for bullet points and list items
        details = []
        for line in lines:
            # Clean up markdown
            clean_line = line.replace('**', '').replace('*', '').strip()
            
            # Match bullet points, dashes, or numbered lists
            if any(clean_line.startswith(prefix) for prefix in ['•', '-', '→', '1.', '2.', '3.', '4.', '5.']):
                # Remove the prefix
                detail = clean_line.lstrip('•-→123456789. ')
                if detail and len(detail) > 10:  # Only substantial details
                    details.append(detail)
        
        # If no details found, extract from paragraphs
        if not details:
            for line in lines[1:]:
                clean_line = line.replace('**', '').replace('*', '').strip()
                if len(clean_line) > 20 and not clean_line.startswith('#'):
                    details.append(clean_line)
                    if len(details) >= 5:
                        break
        
        # Extract recommended actions - look for action-oriented items
        recommended_actions = []
        in_actions = False
        
        for line in lines:
            clean_line = line.replace('**', '').replace('*', '').strip()
            
            # Detect action section
            if any(keyword in clean_line.lower() for keyword in ['what to do', 'recommended', 'action', 'solution', 'steps', 'resolve']):
                in_actions = True
                continue
            
            # Extract actions
            if in_actions and any(clean_line.startswith(prefix) for prefix in ['•', '-', '→', '1.', '2.', '3.', '4.', '5.']):
                action = clean_line.lstrip('•-→123456789. ')
                if action and len(action) > 10:
                    recommended_actions.append(action)
        
        # Fallback recommended actions if none found
        if not recommended_actions:
            recommended_actions = [
                "Check the fields[] array in the error response for specific validation errors",
                "Verify all required parameters are included in the request",
                "Validate data types match the API specification",
                "Review the API documentation for the correct request format",
                "Contact support with the correlationId if the issue persists"
            ]
        
        # Build sources
        sources = []
        for source_meta in result.get("sources", []):
            url = source_meta.get("url", "https://docs-hotel.prod.zentrumhub.com")
            title = source_meta.get("title", "ZentrumHub API Documentation")
            
            sources.append(Source(
                title=title,
                section="error_codes",
                url=url,
                snippet=summary[:150]
            ))
        
        return ExplainResponse(
            summary=summary,
            details=details[:5],
            recommended_actions=recommended_actions[:5],
            sources=sources,
            confidence=result["confidence"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing explanation: {str(e)}")


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

@router.get("/analytics/top-queries/by-client")
async def top_queries_by_client(client_id: str, limit: int = 5):
    """Get top queries by specific client"""
    client_queries = analytics.client_query_counter.get(client_id, {})
    data = sorted(client_queries.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        "client_id": client_id,
        "total_queries": sum(client_queries.values()),
        "top_queries": [{"question": q, "count": c} for q, c in data]
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

@router.post("/analytics/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for a chat response"""
    try:
        # Create feedback entry
        feedback_entry = {
            "message_id": request.message_id,
            "conversation_id": request.conversation_id,
            "question": request.question,
            "answer": request.answer,
            "feedback": request.feedback,
            "confidence": request.confidence,
            "timestamp": request.timestamp
        }
        
        # Log feedback
        analytics.log_feedback(feedback_entry)
        
        return FeedbackResponse(
            status="success",
            message="Feedback recorded successfully",
            message_id=request.message_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@router.get("/analytics/feedback-stats")
async def feedback_stats():
    """Get feedback statistics"""
    return analytics.get_feedback_stats()

@router.get("/analytics/negative-feedback")
async def negative_feedback(limit: int = 20):
    """Get recent negative feedback for improvement"""
    return {
        "negative_feedback": analytics.get_negative_feedback(limit)
    }
