# System Architecture

## Overview
ZentrumHub Chatbot is a 3-layer architecture with live documentation fetching and Gemini 2.5 Pro integration.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / FRONTEND                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: CONTROLLER                           │ 
│                  (app/controllers/chat_controller.py)            │
│                                                                   │
│  Endpoints:                                                       │
│  • POST /api/chat              - Main chat                       │
│  • POST /api/explain           - Error explanations              │
│  • POST /api/analytics/feedback - Submit feedback                │
│  • GET  /api/analytics/*       - Analytics & stats               │
│  • GET  /api/health            - Health check                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 2: RAG SERVICE                          │
│                  (app/services/rag_service.py)                   │
│                                                                   │
│  Methods:                                                         │
│  • generate_answer()    - Main RAG pipeline                      │
│  • explain_error()      - Error-specific RAG                     │
│  • build_prompt()       - Prompt engineering                     │
│  • build_explain_prompt() - Error prompt engineering             │
│                                                                   │
│  Uses:                                                            │
│  • DocumentationFetcher - Live doc retrieval                     │
│  • LLM Client          - AI generation                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  DOCUMENTATION FETCHER   │  │    LAYER 3: LLM CLIENT   │
│  (doc_fetcher.py)        │  │  (llm/gemini_client.py)  │
│                          │  │                          │
│  • Fetches from:         │  │  • Gemini 2.5 Pro        │
│    - /docs/ (8 APIs)     │  │  • Max tokens: 8192      │
│    - /recipes/ (15)      │  │  • Temperature: 0.7      │
│  • Keyword matching      │  │  • Timeout: 60s          │
│  • Score-based routing   │  │                          │
└──────────┬───────────────┘  └──────────┬───────────────┘
           │                             │
           ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  LIVE DOCUMENTATION      │  │  GOOGLE GEMINI API       │
│  docs-hotel.prod.        │  │  generativelanguage.     │
│  zentrumhub.com          │  │  googleapis.com          │
└──────────────────────────┘  └──────────────────────────┘
```

## Data Flow

### 1. Chat Request Flow
```
User Question
    ↓
Controller receives request
    ↓
RAG Service: generate_answer()
    ↓
DocumentationFetcher: fetch_documentation()
    ↓
Fetch from live docs (https://docs-hotel.prod.zentrumhub.com)
    ↓
Build prompt with live context
    ↓
Gemini 2.5 Pro generates answer
    ↓
Return response with sources
    ↓
Log analytics
    ↓
Return to user
```

### 2. Explain Request Flow
```
Error Code/Message
    ↓
Controller receives request
    ↓
RAG Service: explain_error()
    ↓
Fetch from MULTIPLE API pages (for error codes)
    ↓
Combine error documentation
    ↓
Build specialized error prompt
    ↓
Gemini 2.5 Pro generates explanation
    ↓
Parse structured response (summary, details, actions)
    ↓
Return to user
```

### 3. Feedback Flow
```
User submits feedback
    ↓
Controller receives feedback
    ↓
Analytics: log_feedback()
    ↓
Append to feedback_data array
    ↓
Save to analytics_data.json
    ↓
Return confirmation
```

## Components

### Controllers (Layer 1)
**File:** `app/controllers/chat_controller.py`

**Responsibilities:**
- HTTP request/response handling
- Input validation
- Latency measurement
- Analytics logging
- Error handling

**Endpoints:**
- `/api/chat` - Main chat
- `/api/explain` - Error explanations
- `/api/analytics/feedback` - Feedback submission
- `/api/analytics/feedback-stats` - Feedback statistics
- `/api/analytics/top-queries` - Query analytics
- `/api/analytics/unanswered-questions` - Low confidence queries

### RAG Service (Layer 2)
**File:** `app/services/rag_service.py`

**Responsibilities:**
- Orchestrate RAG pipeline
- Fetch live documentation
- Build context-aware prompts
- Generate answers via LLM
- Handle error explanations

**Key Features:**
- NO static knowledge base
- ALWAYS fetches live documentation
- Query-specific routing
- Specialized error handling

### Documentation Fetcher
**File:** `app/services/doc_fetcher.py`

**Responsibilities:**
- Fetch from live documentation
- Keyword-based routing
- Score-based page selection
- Support both /docs/ and /recipes/

**Coverage:**
- 8 API documentation pages
- 15 recipe workflow pages
- 110+ keyword mappings

### LLM Client (Layer 3)
**File:** `app/llm/gemini_client.py`

**Responsibilities:**
- Interface with Gemini 2.5 Pro
- Handle API calls
- Manage timeouts
- Error handling

**Configuration:**
- Model: `gemini-2.5-pro`
- Max tokens: 8192
- Temperature: 0.7
- Timeout: 60s

### Analytics
**File:** `app/utils/analytics.py`

**Responsibilities:**
- Track queries
- Track feedback
- Persistent storage
- Statistics calculation

**Storage:**
- File: `analytics_data.json`
- Auto-load on startup
- Auto-save on changes

## Documentation Coverage

### API Documentation (/docs/)
1. cancel-api
2. roomrates-api
3. direct-rooms-and-rates
4. book-api
5. search-api
6. static-content-api
7. autosuggest-api
8. price-api

### Recipe Documentation (/recipes/)
1. search-init
2. search-results
3. search-results-polling
4. roomsandrates
5. pricebyrecommendation
6. book
7. blocking-search
8. zentrum-connect-download-content
9. zentrum-connect-hotel-search
10. zentrum-connect-room-rates
11. zentrum-connect-price
12. zentrum-connect-book
13. zentrum-connect-retreive-booking
14. cancel-booking
15. zentrum-connect-rate-combinability

## Key Design Decisions

### 1. Live Documentation Only
- NO static knowledge base files
- ALWAYS fetch from live documentation
- Ensures answers are always current
- Self-updating system

### 2. 3-Layer Architecture
- Clear separation of concerns
- Controller → Service → Client
- Easy to test and maintain
- Scalable design

### 3. Persistent Analytics
- Survives server restarts
- JSON file storage
- Auto-save on changes
- Historical tracking

### 4. Feedback System
- Track user satisfaction
- Identify problem areas
- Data-driven improvements
- Positive/negative tracking

### 5. Gemini 2.5 Pro
- Advanced reasoning
- High quality answers
- 8192 token output
- Thinking mode support

## Configuration

### Environment Variables (.env)
```
GEMINI_API_KEY=your_api_key_here
```

### Config (app/config.py)
```python
GEMINI_MODEL = "gemini-2.5-pro"
MAX_OUTPUT_TOKENS = 8192
TEMPERATURE = 0.7
TOP_K_DOCUMENTS = 5
```

## Deployment

### Start Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Access Points
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Testing

### Test Scripts
1. `test_server.py` - Import validation
2. `test_feedback.py` - Feedback endpoints
3. `test_explain_endpoint.py` - Error explanations
4. `test_recipes_coverage.py` - Recipe accessibility

### Run Tests
```bash
python test_server.py
python test_feedback.py
python test_explain_endpoint.py
python test_recipes_coverage.py
```

## Performance

### Typical Response Times
- Chat: 2-5 seconds
- Explain: 3-6 seconds
- Analytics: <100ms
- Health: <10ms

### Bottlenecks
1. Live documentation fetching (1-2s)
2. Gemini API call (1-3s)
3. Network latency

### Optimizations
- Async/await throughout
- Efficient keyword matching
- Minimal data processing
- Direct API calls
