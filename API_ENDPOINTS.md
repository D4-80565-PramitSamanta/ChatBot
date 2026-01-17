# ZentrumHub Chatbot API Endpoints

## Base URL
```
http://localhost:8000
```

## Health & Status

### GET /api/health
Check server health and status
```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok",
  "service": "zentrumhub-chatbot",
  "version": "1.0.0",
  "llm": "gemini-2.5-pro"
}
```

---

## Chat Endpoints

### POST /api/chat
Main chat endpoint for asking questions
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I search for hotels?",
    "conversation_id": "conv-123",
    "history": []
  }'
```

Response:
```json
{
  "answer": "To search for hotels...",
  "confidence": "high",
  "sources": [...],
  "tokens_used": null,
  "latency_ms": 1234,
  "service_used": "gemini_2.5_pro"
}
```

### POST /api/explain
Explain error codes and API issues
```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "error_code",
    "content": "Error 4004: Hotel sold out",
    "client_id": "client-123"
  }'
```

Response:
```json
{
  "summary": "Error 4004 means...",
  "details": ["...", "..."],
  "recommended_actions": ["...", "..."],
  "sources": [...],
  "confidence": "high"
}
```

### GET /api/suggested-questions
Get suggested questions for users
```bash
curl http://localhost:8000/api/suggested-questions
```

---

## Analytics Endpoints

### GET /api/analytics/top-queries
Get top queries across all clients
```bash
curl http://localhost:8000/api/analytics/top-queries?limit=10
```

Response:
```json
{
  "total_queries": 150,
  "top_queries": [
    {"question": "How to search?", "count": 25},
    ...
  ]
}
```

### GET /api/analytics/top-queries/by-client
Get top queries for a specific client
```bash
curl http://localhost:8000/api/analytics/top-queries/by-client?client_id=client-123&limit=5
```

Response:
```json
{
  "client_id": "client-123",
  "total_queries": 50,
  "top_queries": [...]
}
```

### GET /api/analytics/unanswered-questions
Get questions with low confidence answers
```bash
curl http://localhost:8000/api/analytics/unanswered-questions?limit=20
```

Response:
```json
{
  "total_unanswered": 10,
  "questions": [
    {
      "question": "...",
      "count": 5,
      "first_seen": "2026-01-16T10:00:00",
      "last_seen": "2026-01-16T15:00:00"
    }
  ]
}
```

---

## Feedback Endpoints

### POST /api/analytics/feedback
Submit user feedback for a chat response
```bash
curl -X POST http://localhost:8000/api/analytics/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg-123",
    "conversation_id": "conv-123",
    "question": "How to cancel?",
    "answer": "To cancel...",
    "feedback": "positive",
    "confidence": "high",
    "timestamp": "2026-01-16T18:10:25.876Z"
  }'
```

### POST /api/feedback (Alias)
Alternative endpoint for feedback submission (same as /api/analytics/feedback)
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg-123",
    "conversation_id": "conv-123",
    "question": "How to cancel?",
    "answer": "To cancel...",
    "feedback": "positive",
    "confidence": "high",
    "timestamp": "2026-01-16T18:10:25.876Z"
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "message_id": "msg-123"
}
```

### GET /api/analytics/feedback-stats
Get feedback statistics
```bash
curl http://localhost:8000/api/analytics/feedback-stats
```

Response:
```json
{
  "total_feedback": 100,
  "positive": 85,
  "negative": 15,
  "positive_rate": 85.0,
  "recent_feedback": [...]
}
```

### GET /api/analytics/negative-feedback
Get recent negative feedback for improvement
```bash
curl http://localhost:8000/api/analytics/negative-feedback?limit=20
```

Response:
```json
{
  "negative_feedback": [
    {
      "message_id": "msg-456",
      "question": "...",
      "answer": "...",
      "timestamp": "..."
    }
  ]
}
```

---

## Documentation Coverage

### API Documentation (docs/)
- Cancel API
- Rooms and Rates API
- Direct Rooms and Rates API
- Book API
- Search API
- Static Content API
- Autosuggest API
- Price API

### Recipe Documentation (recipes/)
- search-init
- search-results
- search-results-polling
- roomsandrates
- pricebyrecommendation
- book
- blocking-search
- zentrum-connect-download-content
- zentrum-connect-hotel-search
- zentrum-connect-room-rates
- zentrum-connect-price
- zentrum-connect-book
- zentrum-connect-retreive-booking
- cancel-booking
- zentrum-connect-rate-combinability

### API Reference Documentation (reference/) ⭐ NEW
- post_api-hotel-search - Search API specifications
- post_api-hotel-hotelid-roomsandrates-token - Rooms & Rates API specs
- post_api-hotel-hotelid-roomsandrates - Direct Rooms & Rates specs
- post_api-hotel-hotelid-price-recommendationid - Price API specs
- post_api-hotel-booking - Booking API specifications
- post_api-hotel-booking-bookingid-cancel - Cancel API specs
- get_api-hotel-booking-bookingid - Get Booking specs
- post_api-hotel-static-content - Static Content API specs
- get_api-hotel-autosuggest - Autosuggest API specs

**Total Coverage: 8 docs + 15 recipes + 9 references = 32 documentation pages**

---

## Testing

### Test Feedback Flow
```bash
python test_feedback.py
```

### Test Explain Endpoint
```bash
python test_explain_endpoint.py
```

### Test Recipe Coverage
```bash
python test_recipes_coverage.py
```

### Test Reference Documentation ⭐ NEW
```bash
python test_reference_docs.py
```

### Test Server
```bash
python test_server.py
```

---

## Swagger Documentation
Interactive API documentation available at:
```
http://localhost:8000/docs
```

---

## Starting the Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

Or use the batch file:
```bash
start.bat
```
