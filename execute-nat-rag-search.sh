#!/bin/bash

# NAT-RAG Integration Execution Script
# Demonstrates how to use NAT with the RAG pipeline

echo "🤖 NVIDIA Agent Toolkit - RAG Pipeline Integration"
echo "================================================="
echo ""

# Check if we're in the NAT container
if [ ! -f "/app/nat-rag-integration.py" ]; then
    echo "❌ Error: nat-rag-integration.py not found in /app/"
    echo "Make sure you're running this from inside the NAT container"
    exit 1
fi

# Test RAG server connectivity
echo "🔍 Testing RAG server connectivity..."
python3 /app/nat-rag-integration.py "Test connection" case_1000230

echo ""
echo "📊 Available search options:"
echo "1. Direct Python search: python3 /app/nat-rag-integration.py '<query>'"
echo "2. Bash script search: ./test-rag-api.sh"
echo "3. Simple search: ./simple-case-search.sh '<query>'"
echo "4. NAT workflow: nat run /app/workflows/nat-rag-workflow-integrated.yml"
echo ""

# Example searches
echo "🎯 Example searches you can run:"
echo ""
echo "# Search for travel expenses:"
echo "python3 /app/nat-rag-integration.py 'Find all travel expenses over \$1000'"
echo ""
echo "# Search for meeting notes:"
echo "python3 /app/nat-rag-integration.py 'Show me all meeting notes from December 2024'"
echo ""
echo "# Search for anomalies:"
echo "python3 /app/nat-rag-integration.py 'Identify any unusual spending patterns or travel gaps'"
echo ""
echo "# Deep analysis:"
echo "python3 /app/nat-rag-integration.py 'Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures'"
echo ""

echo "✅ NAT-RAG integration ready!"
echo "The RAG server at http://10.0.0.25:30081 is accessible from the NAT container"
echo "Collection case_1000230 is ready for searching"
