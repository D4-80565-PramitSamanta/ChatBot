# Changelog

## [Latest Update] - 2026-01-17

### ✨ New Features

#### 1. API Reference Documentation Support ⭐ NEW
- **Added /reference/ documentation source** - Complete API specifications with field-level details
- **9 reference pages** covering all major APIs
- **Highest priority routing** for field/request/schema queries
- **Enhanced scoring** (30+ points for reference matches)
- **Automatic boost** for keywords: field, request, body, parameter, schema, format, how to, create, send

**Reference Pages Added:**
- post_api-hotel-search - Search API specifications
- post_api-hotel-hotelid-roomsandrates-token - Rooms & Rates API specs
- post_api-hotel-hotelid-roomsandrates - Direct Rooms & Rates specs
- post_api-hotel-hotelid-price-recommendationid - Price API specs
- post_api-hotel-booking - Booking API specifications
- post_api-hotel-booking-bookingid-cancel - Cancel API specs
- get_api-hotel-booking-bookingid - Get Booking specs
- post_api-hotel-static-content - Static Content API specs
- get_api-hotel-autosuggest - Autosuggest API specs

**Benefits:**
- Complete request/response specifications
- Field-level data types and descriptions
- Required vs optional field information
- Valid values and constraints
- Example values for all fields

#### 2. Feedback System
- **POST /api/analytics/feedback** - Submit user feedback (positive/negative) for chat responses
- **GET /api/analytics/feedback-stats** - Get comprehensive feedback statistics
  - Total feedback count
  - Positive/negative breakdown
  - Positive rate percentage
  - Recent feedback entries
- **GET /api/analytics/negative-feedback** - Get recent negative feedback for improvement

#### 3. Expanded Recipe Documentation Coverage
Added 15 new recipe pages to the documentation fetcher:

**Search Workflows:**
- search-init
- search-results
- search-results-polling
- blocking-search

**Rooms & Rates Workflows:**
- roomsandrates
- pricebyrecommendation

**Booking Workflows:**
- book
- cancel-booking

**Zentrum Connect Workflows:**
- zentrum-connect-download-content
- zentrum-connect-hotel-search
- zentrum-connect-room-rates
- zentrum-connect-price
- zentrum-connect-book
- zentrum-connect-retreive-booking
- zentrum-connect-rate-combinability

#### 4. Enhanced Keyword Mapping ⭐ UPDATED
- Expanded doc_map with 50+ keywords for better API matching
- Expanded recipes_map with 60+ keywords for workflow matching
- **Added reference_map with 40+ keywords** ⭐ NEW
- Added synonyms and variations for better query understanding
- Improved scoring algorithm with 3-tier priority (reference > recipes > docs)
- **Total: 150+ keyword mappings** ⭐

### 📝 Schema Updates

#### New Models (app/models/schemas.py)
```python
class FeedbackRequest(BaseModel):
    message_id: str
    conversation_id: str
    question: str
    answer: str
    feedback: str  # "positive" or "negative"
    confidence: str
    timestamp: str

class FeedbackResponse(BaseModel):
    status: str
    message: str
    message_id: str
```

### 🔧 Analytics Updates (app/utils/analytics.py)

#### New Methods
- `log_feedback(feedback_entry)` - Store feedback with persistence
- `get_feedback_stats()` - Calculate and return feedback statistics
- `get_negative_feedback(limit)` - Retrieve negative feedback for analysis

#### Enhanced Storage
- Feedback data now persists in `analytics_data.json`
- Auto-loads on startup
- Auto-saves after each feedback submission

### 📚 Documentation Updates

#### New Files
- **API_ENDPOINTS.md** - Complete API reference with curl examples (updated with reference docs)
- **test_feedback.py** - Comprehensive feedback endpoint testing
- **test_recipes_coverage.py** - Recipe page accessibility testing
- **test_reference_docs.py** ⭐ NEW - Reference documentation testing
- **CHANGELOG.md** - This file
- **SUMMARY.md** - Complete implementation summary
- **ARCHITECTURE.md** - System architecture documentation

### 🧪 Testing

#### New Test Scripts
1. **test_feedback.py**
   - Tests positive feedback submission
   - Tests negative feedback submission
   - Tests feedback statistics retrieval
   - Tests negative feedback filtering

2. **test_recipes_coverage.py**
   - Verifies all 15 recipe pages are accessible
   - Tests chatbot with recipe-specific queries
   - Validates documentation fetching

3. **test_reference_docs.py** ⭐ NEW
   - Verifies all 9 reference pages are accessible
   - Tests field-level detail queries
   - Validates reference doc routing
   - Checks request/response schema queries
   - Tests automatic field-detail routing

4. **test_explain_endpoint.py** (existing, enhanced)
   - Tests error code explanations
   - Validates parsing logic
   - Checks response structure

### 🎯 Key Improvements

1. **Complete Documentation Coverage** ⭐ ENHANCED
   - System now covers 8 API docs + 15 recipe workflows + 9 API references
   - **Total of 32 documentation pages** ⭐
   - Comprehensive keyword mapping for accurate retrieval
   - 3-tier priority system for optimal routing

2. **Field-Level API Specifications** ⭐ NEW
   - Complete request/response schemas
   - Data type information for all fields
   - Required vs optional field indicators
   - Valid values and constraints
   - Example values

3. **User Feedback Loop**
   - Track user satisfaction with responses
   - Identify problematic answers
   - Measure chatbot effectiveness
   - Data-driven improvement insights

3. **Persistent Analytics**
   - All analytics survive server restarts
   - Feedback data stored permanently
   - Historical tracking enabled

### 📊 Analytics Data Structure

```json
{
  "query_counter": {...},
  "client_query_counter": {...},
  "unanswered_counter": {...},
  "feedback_data": [
    {
      "message_id": "...",
      "conversation_id": "...",
      "question": "...",
      "answer": "...",
      "feedback": "positive|negative",
      "confidence": "high|medium|low",
      "timestamp": "..."
    }
  ],
  "last_updated": "2026-01-17T..."
}
```

### 🚀 Usage Examples

#### Submit Feedback
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
    "timestamp": "2026-01-17T10:00:00Z"
  }'
```

#### Get Feedback Stats
```bash
curl http://localhost:8000/api/analytics/feedback-stats
```

#### Query Recipe Workflows
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I initialize a search?",
    "conversation_id": "test"
  }'
```

### 🔍 What's Next

Potential future enhancements:
- Feedback comments/notes field
- Feedback categories (accuracy, completeness, clarity)
- Time-based analytics (daily/weekly trends)
- A/B testing support
- Export analytics to CSV/Excel
- Real-time feedback dashboard

---

## Previous Updates

See context transfer summary for complete history of:
- Task 1-7: Core architecture and RAG implementation
- Task 8: /explain endpoint for error codes
- Task 9: Recipe documentation expansion
