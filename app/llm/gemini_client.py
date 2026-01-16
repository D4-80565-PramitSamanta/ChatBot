# app/llm/gemini_client.py
import httpx
import json
from typing import Dict, Any
from app.llm.llm_client import LLMClient
from app.config import config

class GeminiClient(LLMClient):
    """Gemini 2.5 Pro LLM Client"""
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = config.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    async def generate(self, prompt: str) -> str:
        """
        Generate response from Gemini 2.5 Pro
        
        Args:
            prompt: The complete prompt with context
            
        Returns:
            Generated text response
        """
        url = f"{self.base_url}/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": config.TEMPERATURE,
                "topK": config.TOP_K,
                "topP": config.TOP_P,
                "maxOutputTokens": config.MAX_OUTPUT_TOKENS
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=60.0  # Increased timeout for Gemini 2.5 Pro thinking
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract text from response
            if data.get("candidates") and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if candidate.get("content") and candidate["content"].get("parts"):
                    return candidate["content"]["parts"][0]["text"]
            
            raise ValueError("Unexpected response format from Gemini")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": "Google Gemini",
            "model": self.model,
            "version": "2.5-pro",
            "capabilities": [
                "Advanced reasoning",
                "1M token context",
                "Thinking mode",
                "Multi-modal support"
            ]
        }
