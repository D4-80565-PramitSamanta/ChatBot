# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    """Single message in conversation history"""
    role: str = Field(..., example="user")
    content: str = Field(..., example="What is ZentrumHub?")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., example="How do I search for hotels?")
    conversation_id: Optional[str] = Field(None, example="conv-123")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class ExplainRequest(BaseModel):
    """Request model for explain endpoint"""
    input_type: str = Field(..., example="error_code")
    content: str = Field(..., example="Error 4004: The hotel you selected is sold out")
    client_id: Optional[str] = Field(None, example="client-123")

class Source(BaseModel):
    """Source document information"""
    title: str
    section: str
    url: str
    snippet: str

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    confidence: str
    sources: List[Source]
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    service_used: Optional[str] = "gemini_2.5_pro"

class ExplainResponse(BaseModel):
    """Response model for explain endpoint"""
    summary: str
    details: List[str]
    recommended_actions: List[str]
    sources: List[Source]
    confidence: str

class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint"""
    message_id: str = Field(..., example="29170d2e-8522-406d-8cee-2adaba85e252")
    conversation_id: str = Field(..., example="9f5fffa1-3cef-4a32-9d09-a65a5b86dee1")
    question: str = Field(..., example="how to cancel a booking")
    answer: str = Field(..., example="To cancel a booking...")
    feedback: str = Field(..., example="positive")  # positive or negative
    confidence: str = Field(..., example="high")
    timestamp: str = Field(..., example="2026-01-16T18:10:25.876Z")

class FeedbackResponse(BaseModel):
    """Response model for feedback submission"""
    status: str
    message: str
    message_id: str
