# app/llm/llm_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass
