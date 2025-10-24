#!/bin/bash

# Simple Case Collection Search Script
# Easy to modify for different queries

RAG_SERVER_URL="http://10.0.0.25:30081"
COLLECTION_NAME="case_1000230"

# Default query - you can change this
QUERY="${1:-Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures}"

echo "🔍 Searching Case Collection: $COLLECTION_NAME"
echo "=============================================="
echo ""
echo "Query: $QUERY"
echo ""

curl -X POST $RAG_SERVER_URL/generate \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "'"$QUERY"'"
      }
    ],
    "use_knowledge_base": true,
    "collection_names": ["'$COLLECTION_NAME'"],
    "max_tokens": 2000,
    "temperature": 0.1
  }' \
  -s

echo ""
echo "✅ Search completed!"
