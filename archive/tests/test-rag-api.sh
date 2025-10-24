#!/bin/bash

# RAG Server API Test Script
# Tests the RAG server with collection ending in 230

RAG_SERVER_URL="http://10.0.0.25:30081"
COLLECTION_NAME="case_1000230"

echo "🧪 Testing RAG Server API"
echo "========================="
echo ""
echo "Server: $RAG_SERVER_URL"
echo "Collection: $COLLECTION_NAME"
echo ""

# Test with your query
echo "📝 Testing with your query..."
echo "Raw response:"
echo "============="
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
    "temperature": 0.1
  }' \
  -s

echo ""
echo "============="
echo "✅ Test completed!"
