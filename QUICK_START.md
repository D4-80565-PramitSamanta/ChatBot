# Quick Start Guide

## 🚀 Start the Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## 📊 Access Points
- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/health

## 🧪 Run Tests
```bash
# Test everything
python test_server.py
python test_feedback.py
python test_recipes_coverage.py
python test_reference_docs.py
python test_explain_endpoint.py
```

## 💬 Example Queries

### Field-Level Details (fetches from /reference/)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What fields are required in the rooms and rates request body?", "conversation_id": "test"}'
```

### Workflow Guide (fetches from /recipes/)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain the booking workflow", "conversation_id": "test"}'
```

### Error Explanation
```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"input_type": "error_code", "content": "4004", "client_id": "test"}'
```

### Submit Feedback
```bash
# Simple endpoint (recommended for frontend)
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg-123",
    "conversation_id": "conv-123",
    "question": "test",
    "answer": "test answer",
    "feedback": "positive",
    "confidence": "high",
    "timestamp": "2026-01-17T10:00:00Z"
  }'

# Alternative endpoint (also works)
curl -X POST http://localhost:8000/api/analytics/feedback \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Get Feedback Stats
```bash
curl http://localhost:8000/api/analytics/feedback-stats
```

## 📚 Documentation Coverage

**32 Total Pages:**
- 8 API Guides (/docs/)
- 15 Workflow Recipes (/recipes/)
- 9 API References (/reference/) ⭐

**3-Tier Priority:**
1. Reference (field-level specs)
2. Recipes (workflows)
3. Docs (concepts)

## 🎯 Query Tips

### For Field Details → Use "field", "request", "schema"
✅ "What fields are in the booking request?"
✅ "Show me the request schema"
✅ "What parameters are required?"

### For Workflows → Use "workflow", "process", "steps"
✅ "Explain the booking workflow"
✅ "What is the search process?"
✅ "Show me the steps to book"

### For Concepts → Use general questions
✅ "What is the cancel API?"
✅ "Tell me about rooms and rates"
✅ "What does error 4004 mean?"

## 📁 Key Files

**Core:**
- `app/main.py` - FastAPI app
- `app/controllers/chat_controller.py` - Endpoints
- `app/services/rag_service.py` - RAG logic
- `app/services/doc_fetcher.py` - Live docs fetching
- `app/llm/gemini_client.py` - Gemini 2.5 Pro

**Config:**
- `.env` - API keys
- `app/config.py` - Settings

**Data:**
- `analytics_data.json` - Persistent analytics

**Tests:**
- `test_feedback.py`
- `test_recipes_coverage.py`
- `test_reference_docs.py`
- `test_explain_endpoint.py`

**Docs:**
- `API_ENDPOINTS.md` - API reference
- `ARCHITECTURE.md` - System design
- `REFERENCE_DOCS_GUIDE.md` - Reference docs guide
- `SUMMARY.md` - Implementation summary
- `CHANGELOG.md` - Change history

## 🔑 Environment Variables

Create `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## ✅ Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "zentrumhub-chatbot",
  "version": "1.0.0",
  "llm": "gemini-2.5-pro"
}
```

## 🎉 You're Ready!

The system is fully configured with:
- ✅ Live documentation fetching
- ✅ 32 documentation pages
- ✅ 3-tier routing system
- ✅ Field-level specifications
- ✅ Feedback tracking
- ✅ Persistent analytics
- ✅ Error explanations
- ✅ Gemini 2.5 Pro integration
