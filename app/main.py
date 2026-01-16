# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.llm.gemini_client import GeminiClient
from app.services.rag_service import RAGService
from app.controllers import chat_controller

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION
)

# CORS middleware - Allow all origins for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize services
# Layer 3: LLM Client
llm_client = GeminiClient()

# Layer 2: RAG Service
rag_service = RAGService(llm_client)

# Layer 1: Controller (inject RAG service)
chat_controller.set_rag_service(rag_service)
app.include_router(chat_controller.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZentrumHub Documentation Assistant API",
        "version": config.API_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
