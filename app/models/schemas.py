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
