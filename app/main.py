# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.llm.gemini_client import GeminiClient
from app.services.rag_service import RAGService
from app.controllers import chat_controller

# Initialize FastAPI app with comprehensive OpenAPI metadata
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="""
    AI-powered chatbot API for ZentrumHub hotel booking platform documentation.
    
    This API provides intelligent assistance for developers integrating with ZentrumHub APIs,
    offering comprehensive documentation coverage, error explanations, and analytics.
    
    ## Features
    - **AI-Powered Chat**: Get instant answers about ZentrumHub APIs
    - **Error Explanation**: Understand and resolve API errors  
    - **Analytics**: Track usage patterns and improve documentation
    - **Feedback System**: Continuous improvement through user feedback
    
    ## Coverage
    - **Zentrum Booking Engine APIs**: Search, RoomsAndRates, Booking, Cancellation
    - **Zentrum Connect APIs**: Direct access, Rate combinability, Multi-room bookings
    - **Static Content APIs**: Hotel information, Images, Facilities
    - **Location APIs**: Autosuggest, Geocoding, Search regions
    """,
    contact={
        "name": "ZentrumHub Support",
        "url": "https://zentrumhub.com/support",
        "email": "support@zentrumhub.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8080",
            "description": "Local development server"
        },
        {
            "url": "https://api.zentrumhub-docs.com", 
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "General",
            "description": "General API information and root endpoints"
        },
        {
            "name": "Health", 
            "description": "Health check and status endpoints"
        },
        {
            "name": "Chat",
            "description": "AI chat and assistance endpoints for ZentrumHub API help"
        },
        {
            "name": "Explanation",
            "description": "Error and issue explanation endpoints"
        },
        {
            "name": "Analytics",
            "description": "Usage analytics and insights for improving documentation"
        },
        {
            "name": "Feedback",
            "description": "User feedback collection for continuous improvement"
        }
    ],
    openapi_tags=[
        {
            "name": "Chat",
            "description": "Main chat functionality",
            "externalDocs": {
                "description": "ZentrumHub API Documentation",
                "url": "https://docs-hotel.prod.zentrumhub.com"
            }
        }
    ]
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

@app.get("/", tags=["General"])
async def root():
    """
    API Root Endpoint
    
    Returns basic API information and available endpoints.
    Use this to verify the API is running and get navigation links.
    """
    return {
        "message": "ZentrumHub Documentation Assistant API",
        "version": config.API_VERSION,
        "description": "AI-powered chatbot for ZentrumHub API documentation",
        "docs": "/docs",
        "redoc": "/redoc", 
        "health": "/api/health",
        "chat": "/api/chat",
        "explain": "/api/explain",
        "analytics": "/api/analytics",
        "coverage": {
            "booking_engine_apis": ["search-init", "search-results", "roomsandrates", "price", "book"],
            "connect_apis": ["hotel-search", "room-rates", "price-recheck", "book", "cancel", "rate-combinability"],
            "content_apis": ["static-content", "autosuggest"],
            "total_endpoints": 32
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
