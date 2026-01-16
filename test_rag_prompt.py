#!/usr/bin/env python
"""Test script to show RAG prompt generation"""

import json
from app.config import config

# Simulate the RAG process
question = "tell me about hotelapi roomsandrates"

print("=" * 80)
print("RAG PROMPT GENERATION TEST")
print("=" * 80)
print(f"\nUser Question: {question}")
print("\n" + "=" * 80)

# Step 1: Load documents
print("\nSTEP 1: Loading documents from knowledge base...")
with open(config.KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
    kb = json.load(f)
    print(f"✓ Loaded {len(kb)} sections from knowledge base")

# Step 2: Search for relevant documents (simulate keyword matching)
print(f"\nSTEP 2: Searching for documents matching: '{question}'")
query_lower = question.lower()
query_words = query_lower.split()
print(f"Search keywords: {query_words}")

scored_docs = []
for key, value in kb.items():
    if isinstance(value, dict):
        text = f"{value.get('title', key)}\n{json.dumps(value, indent=2)}"
    else:
        text = f"{key}\n{json.dumps(value, indent=2)}"
    
    doc_lower = text.lower()
    score = 0
    
    # Count matching words
    for word in query_words:
        if word in doc_lower:
            score += 1
    
    # Boost for exact phrase match
    if query_lower in doc_lower:
        score += 10
    
    if score > 0:
        scored_docs.append({
            "key": key,
            "text": text,
            "score": score
        })

# Sort by score
scored_docs.sort(key=lambda x: x["score"], reverse=True)
top_3 = scored_docs[:3]

print(f"\n✓ Found {len(scored_docs)} matching documents")
print(f"✓ Top 3 documents selected:")
for i, doc in enumerate(top_3, 1):
    print(f"   {i}. {doc['key']} (score: {doc['score']})")

# Step 3: Build the prompt
print("\n" + "=" * 80)
print("STEP 3: Building prompt for Gemini 2.5 Flash")
print("=" * 80)

context = "\n\n---\n\n".join([
    f"[Document {i + 1}]\n{doc['text']}"
    for i, doc in enumerate(top_3)
])

prompt = f"""You are an expert assistant for ZentrumHub's Hotel API documentation.

RELEVANT DOCUMENTATION:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based ONLY on the documentation provided above
- Be specific and include API endpoints, parameters, and error codes when relevant
- Format your response with markdown for better readability
- If the answer is not in the documentation, say so clearly
- Be concise but comprehensive

ANSWER:"""

print("\n" + "=" * 80)
print("FINAL PROMPT SENT TO GEMINI 2.5 FLASH:")
print("=" * 80)
print(prompt)
print("\n" + "=" * 80)
print(f"Prompt length: {len(prompt)} characters")
print(f"Estimated tokens: ~{len(prompt.split())}")
print("=" * 80)
