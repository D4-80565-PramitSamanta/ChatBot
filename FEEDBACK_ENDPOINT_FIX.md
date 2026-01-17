# Feedback Endpoint Fix

## Issue
Frontend was calling `/api/feedback` but the endpoint was only available at `/api/analytics/feedback`, resulting in 404 errors.

## Solution
Added an alias endpoint `/api/feedback` that routes to the same handler as `/api/analytics/feedback`.

## Changes Made

### 1. Added Alias Endpoint
**File:** `app/controllers/chat_controller.py`

```python
@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback_alias(request: FeedbackRequest):
    """Submit user feedback - Alias for /analytics/feedback"""
    return await submit_feedback(request)
```

### 2. Both Endpoints Now Work

**Option 1: Simple endpoint (recommended for frontend)**
```bash
POST /api/feedback
```

**Option 2: Full path (also works)**
```bash
POST /api/analytics/feedback
```

Both endpoints accept the same request body and return the same response.

## Request Format

```json
{
  "message_id": "c56ab562-7667-46fa-bfc3-7018defa0ffd",
  "conversation_id": "07ea9810-3b29-4b54-890c-d0acef50f8f7",
  "question": "tell me about base rate and total rate",
  "answer": "Based on the documentation provided...",
  "feedback": "positive",
  "confidence": "high",
  "timestamp": "2026-01-16T18:48:03.096Z"
}
```

## Response Format

```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "message_id": "c56ab562-7667-46fa-bfc3-7018defa0ffd"
}
```

## Testing

### Quick Test
```bash
python test_feedback_alias.py
```

This will:
1. Test the original `/api/analytics/feedback` endpoint
2. Test the new `/api/feedback` alias
3. Verify feedback was saved
4. Show feedback statistics

### Manual Test with curl

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "test-123",
    "conversation_id": "conv-123",
    "question": "test question",
    "answer": "test answer",
    "feedback": "positive",
    "confidence": "high",
    "timestamp": "2026-01-17T10:00:00Z"
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "message_id": "test-123"
}
```

## Frontend Integration

### JavaScript/Fetch Example

```javascript
// Submit feedback
async function submitFeedback(messageId, conversationId, question, answer, feedback, confidence) {
  const response = await fetch('http://localhost:8000/api/feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message_id: messageId,
      conversation_id: conversationId,
      question: question,
      answer: answer,
      feedback: feedback, // "positive" or "negative"
      confidence: confidence,
      timestamp: new Date().toISOString()
    })
  });
  
  const data = await response.json();
  console.log('Feedback submitted:', data);
  return data;
}

// Usage
submitFeedback(
  'msg-123',
  'conv-123',
  'How to cancel?',
  'To cancel a booking...',
  'positive',
  'high'
);
```

### React Example

```jsx
const submitFeedback = async (messageId, conversationId, question, answer, feedback, confidence) => {
  try {
    const response = await fetch('http://localhost:8000/api/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message_id: messageId,
        conversation_id: conversationId,
        question,
        answer,
        feedback,
        confidence,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Feedback submitted successfully:', data);
    return data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
};
```

## Verification

After starting the server, verify both endpoints work:

```bash
# Start server
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, test the alias
python test_feedback_alias.py
```

You should see:
- ✓ Original endpoint works
- ✓ Alias endpoint works
- ✓ Feedback was saved
- ✓ Statistics updated

## Documentation Updated

The following files have been updated to reflect both endpoints:
- `API_ENDPOINTS.md` - Added alias endpoint documentation
- `SUMMARY.md` - Updated endpoint count (now 12 total)
- `QUICK_START.md` - Shows both endpoints with recommendation
- `test_feedback_alias.py` - New test script for verification

## Status

✅ **FIXED** - Frontend can now use `/api/feedback` successfully!

Both endpoints are fully functional and persist feedback to `analytics_data.json`.
