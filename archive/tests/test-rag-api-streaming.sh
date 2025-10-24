#!/bin/bash

# RAG Server API Test Script with Streaming Control
# Tests the RAG server with collection ending in 230

RAG_SERVER_URL="http://10.0.0.25:30081"
COLLECTION_NAME="case_1000230"

echo "🧪 Testing RAG Server API with Streaming Control"
echo "==============================================="
echo ""
echo "Server: $RAG_SERVER_URL"
echo "Collection: $COLLECTION_NAME"
echo ""

# Test with streaming (default behavior)
echo "📝 Testing with STREAMING ENABLED (default)..."
echo "Raw streaming response:"
echo "======================"
curl -X POST $RAG_SERVER_URL/generate \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures"
      }
    ],
    "use_knowledge_base": true,
    "collection_names": ["'$COLLECTION_NAME'"],
    "max_tokens": 2000,
    "temperature": 0.1,
    "stream": true
  }' \
  -s

echo ""
echo "======================"
echo ""

# Test without streaming (if supported)
echo "📝 Testing with STREAMING DISABLED..."
echo "Non-streaming response:"
echo "======================"
curl -X POST $RAG_SERVER_URL/generate \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures"
      }
    ],
    "use_knowledge_base": true,
    "collection_names": ["'$COLLECTION_NAME'"],
    "max_tokens": 2000,
    "temperature": 0.1,
    "stream": false
  }' \
  -s

echo ""
echo "======================"
echo "✅ Test completed!"
