# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_TITLE = "ZentrumHub Documentation Assistant"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "AI-powered chatbot with Gemini 2.5 Pro"
    
    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-pro"  # Gemini 2.5 Pro - advanced thinking model
    MAX_OUTPUT_TOKENS = 8192  # Gemini 2.5 Pro supports up to 65,536
    TEMPERATURE = 0.7
    TOP_K = 40
    TOP_P = 0.95
    
    # RAG Configuration
    TOP_K_DOCUMENTS = 5  # Retrieve more documents for better context
    
    # Data Paths
    KNOWLEDGE_BASE_PATH = "knowledge-base.json"
    KNOWLEDGE_BASE_EXTENDED_PATH = "knowledge-base-extended.json"
    COMPLETE_DOCS_PATH = "complete-documentation.json"
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000

config = Config()
