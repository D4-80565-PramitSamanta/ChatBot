# ZentrumHub Documentation Assistant

AI-powered chatbot using **Gemini 2.5 Pro** with RAG (Retrieval-Augmented Generation) for ZentrumHub Hotel API documentation.

## Features

- **Gemini 2.5 Pro**: Advanced thinking model with superior reasoning
- **1M Token Context**: Handle large documentation sets
- **RAG Technology**: Retrieves relevant docs before answering
- **REST API**: FastAPI with automatic Swagger documentation
- **CORS Enabled**: Ready for frontend integration

## Architecture

Clean 3-layer architecture:

```
User → Controller → RAG Service → LLM Client → Gemini 2.5 Pro
```

### Layer 1: Controller (`app/controllers/chat_controller.py`)
- Handles HTTP requests/responses
- Measures latency
- Logs analytics

### Layer 2: RAG Service (`app/services/rag_service.py`)
- Retrieves relevant documents from vector store
- Builds prompts with context
- Orchestrates LLM calls

### Layer 3: LLM Client (`app/llm/gemini_client.py`)
- Communicates with Gemini 2.5 Pro API
- Handles API requests/responses

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

### 3. Prepare Data

Move your documentation files to `data/` directory:
- `data/knowledge-base.json`
- `data/knowledge-base-extended.json`
- `data/complete-documentation.json`

## Running the API

### Start the Server

```bash
start.bat
```

Or manually:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Access Swagger Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## API Endpoints

### Chat Endpoint
```
POST /api/chat
```

Request:
```json
{
  "question": "How do I search for hotels?",
  "conversation_id": "optional-id",
  "history": []
}
```

Response:
```json
{
  "answer": "Detailed answer from Gemini 2.5 Pro...",
  "confidence": "high",
  "sources": [...],
  "latency_ms": 1234,
  "service_used": "gemini_2.5_pro"
}
```

### Other Endpoints
- `GET /api/health` - Health check
- `GET /api/suggested-questions` - Get suggested questions
- `GET /api/analytics/top-queries` - Top queries analytics
- `GET /api/analytics/unanswered-questions` - Unanswered questions

## Project Structure

```
app/
├── main.py                      # FastAPI bootstrap
├── config.py                    # Configuration
├── controllers/
│   └── chat_controller.py       # Layer 1: API endpoints
├── services/
│   └── rag_service.py          # Layer 2: RAG logic
├── llm/
│   ├── llm_client.py           # Abstract LLM interface
│   └── gemini_client.py        # Layer 3: Gemini implementation
├── models/
│   └── schemas.py              # Pydantic models
└── utils/
    └── analytics.py            # Query tracking

data/                            # Documentation files
public/                          # UI files (optional)
logs/                           # Application logs
```

## Testing with Swagger

1. Start the server: `start.bat`
2. Open browser: http://localhost:8000/docs
3. Click on `POST /api/chat`
4. Click "Try it out"
5. Enter your question in the request body
6. Click "Execute"
7. View the response

## Example Questions

- "How do I search for hotels?"
- "How to authenticate API requests?"
- "What does error 429 mean?"
- "Show booking API example"
- "How to cancel a reservation?"

## Technologies

- **FastAPI** - Modern Python web framework
- **Gemini 2.5 Pro** - Google's latest LLM
- **RAG** - Retrieval-Augmented Generation
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
