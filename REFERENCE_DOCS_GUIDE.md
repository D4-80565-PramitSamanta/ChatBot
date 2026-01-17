# Reference Documentation Guide

## Overview
The system now includes **API Reference Documentation** support, providing complete field-level specifications for all ZentrumHub Hotel APIs.

## What's New?

### 3-Tier Documentation System
```
Priority 1: /reference/ - API Specifications (field-level details)
Priority 2: /recipes/   - Workflow Guides (step-by-step)
Priority 3: /docs/      - API Guides (conceptual)
```

### When Each Source is Used

**Reference (/reference/)** - Highest Priority
- Questions about **fields**, **parameters**, **request body**, **schema**
- Questions with "how to create", "how to send", "request format"
- Questions about data types, required fields, optional fields
- Questions about valid values and constraints

**Recipes (/recipes/)** - Medium Priority
- Questions about **workflows**, **processes**, **steps**
- Questions with "how do I", "what is the flow", "workflow"
- Questions about integration patterns

**Docs (/docs/)** - Base Priority
- General API questions
- Conceptual understanding
- Error codes
- API overviews

## Reference Pages Available

### 1. Search API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-search`

**Covers:**
- Complete search request body schema
- All search parameters with data types
- Response structure
- Field descriptions

**Example Queries:**
- "What fields are required for hotel search?"
- "Show me the search API request format"
- "What parameters does the search API accept?"

### 2. Rooms & Rates API (with token)
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-hotelid-roomsandrates-token`

**Covers:**
- Complete request body for rooms and rates
- All field specifications
- Data types for each field
- Required vs optional fields
- Valid values and constraints

**Example Queries:**
- "What fields are in the rooms and rates request body?"
- "How do I create a rooms and rates request?"
- "What is the schema for rooms and rates API?"
- "Explain each field in the rooms and rates request"

### 3. Direct Rooms & Rates API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-hotelid-roomsandrates`

**Covers:**
- Direct rooms and rates request schema
- Field-level specifications
- Differences from token-based API

**Example Queries:**
- "What's the difference between direct rooms and regular rooms API?"
- "Show me the direct rooms request format"

### 4. Price by Recommendation API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-hotelid-price-recommendationid`

**Covers:**
- Price request parameters
- Recommendation ID usage
- Response structure

**Example Queries:**
- "How do I get a price quote?"
- "What parameters does the price API need?"

### 5. Booking API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-booking`

**Covers:**
- Complete booking request body
- Guest information fields
- Payment fields
- All required and optional parameters

**Example Queries:**
- "How do I create a booking request?"
- "What fields are required for booking?"
- "Show me the booking API schema"
- "What guest information is needed?"

### 6. Cancel Booking API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-booking-bookingid-cancel`

**Covers:**
- Cancel request format
- Required parameters
- Response structure

**Example Queries:**
- "How do I cancel a booking?"
- "What's the cancel API request format?"

### 7. Get Booking API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/get_api-hotel-booking-bookingid`

**Covers:**
- Retrieve booking details
- Response structure
- Booking information fields

**Example Queries:**
- "How do I retrieve a booking?"
- "What information is returned when getting a booking?"

### 8. Static Content API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-static-content`

**Covers:**
- Hotel content request parameters
- Content types available
- Response structure

**Example Queries:**
- "How do I get hotel details?"
- "What fields are in the static content request?"

### 9. Autosuggest API
**URL:** `https://docs-hotel.prod.zentrumhub.com/reference/get_api-hotel-autosuggest`

**Covers:**
- Autosuggest query parameters
- Response format
- Location suggestions

**Example Queries:**
- "How does autosuggest work?"
- "What parameters does autosuggest accept?"

## How It Works

### Automatic Routing
The system automatically routes queries to the appropriate documentation source based on keywords:

```python
# High-priority keywords for reference docs
field, request, body, parameter, schema, format
how to create, how to send, request format
data type, required, optional

# These trigger reference doc fetching with +25 score boost
```

### Scoring System
```
Reference Match:
- Exact keyword match: +30 points
- Word-level match: +15 points
- Partial match: +8 points
- Field/request keywords: +25 bonus

Recipe Match:
- Exact keyword match: +20 points
- Word-level match: +10 points
- Partial match: +5 points

Docs Match:
- Exact keyword match: +20 points
- Word-level match: +10 points
- Partial match: +5 points

Winner: Highest score gets fetched
```

## Testing Reference Documentation

### Test Script
```bash
python test_reference_docs.py
```

### What It Tests
1. **Accessibility** - Verifies all 9 reference pages are accessible
2. **Routing** - Tests that field queries route to reference docs
3. **Content** - Validates field-level details are present
4. **Queries** - Tests various query types

### Sample Test Queries
```python
# Should fetch from reference
"What fields are required in the rooms and rates request body?"
"How do I create a booking request?"
"What parameters does the search API accept?"
"Show me the request schema for rooms and rates"

# Should fetch from recipes
"Explain the booking workflow"
"What is the search polling process?"

# Should fetch from docs
"What does error 4004 mean?"
"Tell me about the cancel API"
```

## Example Usage

### Query for Field Details
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What fields are required in the rooms and rates request body?",
    "conversation_id": "test"
  }'
```

### Expected Response
The response will include:
- Complete list of fields
- Data type for each field (string, integer, boolean, array, object)
- Required vs optional indicator
- Description of each field
- Valid values or constraints
- Example values

### Response Source
```json
{
  "answer": "The rooms and rates request body includes the following fields...",
  "confidence": "high",
  "sources": [{
    "title": "Post Api Hotel Hotelid Roomsandrates Token",
    "url": "https://docs-hotel.prod.zentrumhub.com/reference/post_api-hotel-hotelid-roomsandrates-token",
    "section": "reference"
  }]
}
```

## Benefits

### 1. Complete Field Information
- Every field documented with data type
- Required vs optional clearly marked
- Valid values and constraints listed
- Example values provided

### 2. Better Request Construction
- Developers can see exact request format
- No guessing about field names or types
- Clear understanding of what's required

### 3. Reduced Errors
- Fewer validation errors
- Correct data types from the start
- Understanding of constraints upfront

### 4. Faster Integration
- Complete specifications in one place
- No need to search multiple pages
- Clear examples and schemas

## Keywords That Trigger Reference Docs

### Primary Keywords
- `field`, `fields`
- `request`, `request body`, `request format`
- `parameter`, `parameters`
- `schema`, `request schema`
- `body`, `request body`
- `format`, `data format`

### Action Keywords
- `how to create`
- `how to send`
- `how to make`
- `how to construct`
- `show me the format`
- `what's the structure`

### API-Specific Keywords
- `roomsandrates` + any field keyword
- `booking` + any field keyword
- `search` + any field keyword
- `cancel` + any field keyword

## Tips for Best Results

### 1. Be Specific About Fields
❌ "Tell me about the booking API"
✅ "What fields are required in the booking request body?"

### 2. Use Field-Related Keywords
❌ "How does booking work?"
✅ "Show me the booking request schema"

### 3. Ask About Data Types
✅ "What data type is the checkIn field?"
✅ "What are the required parameters for search?"

### 4. Request Examples
✅ "Show me an example booking request"
✅ "What's the format of the rooms and rates request?"

## Coverage Summary

**Total Documentation Pages: 32**
- 8 API Guides (/docs/)
- 15 Workflow Recipes (/recipes/)
- 9 API References (/reference/) ⭐ NEW

**Total Keywords: 150+**
- 50+ for API guides
- 60+ for recipes
- 40+ for references ⭐ NEW

**Priority System:**
1. Reference (highest) - Field-level specs
2. Recipes (medium) - Workflows
3. Docs (base) - Concepts

## Future Enhancements

Potential improvements:
- Add more reference pages as APIs expand
- Include request/response examples in reference
- Add validation rules documentation
- Include rate limits per endpoint
- Add authentication details per API
