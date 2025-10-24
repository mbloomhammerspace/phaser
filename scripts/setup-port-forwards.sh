#!/bin/bash

# Setup port-forwards for NeMo Agent Toolkit integration
# This script should be run on the jumphost (132.145.204.155)

echo "🚀 Setting up port-forwards for NeMo Agent Toolkit integration..."

# Kill any existing port-forwards
pkill -f "kubectl port-forward" || true

# Port-forward Milvus (GRPC and HTTP)
echo "Setting up Milvus port-forwards..."
kubectl port-forward svc/milvus 19530:19530 &
kubectl port-forward svc/milvus 9091:9091 &

# Port-forward RAG Server
echo "Setting up RAG Server port-forward..."
kubectl port-forward svc/rag-server 8081:8081 &

# Port-forward NIM (if available)
echo "Setting up NIM port-forward..."
kubectl port-forward svc/nim-llm 8000:8000 &

# Wait for port-forwards to establish
sleep 5

echo "✅ Port-forwards established:"
echo "  - Milvus GRPC: localhost:19530"
echo "  - Milvus HTTP: localhost:9091" 
echo "  - RAG Server: localhost:8081"
echo "  - NIM: localhost:8000"

echo "🔍 Testing connectivity..."
timeout 3 telnet localhost 19530 && echo "✅ Milvus GRPC accessible" || echo "❌ Milvus GRPC not accessible"
timeout 3 telnet localhost 9091 && echo "✅ Milvus HTTP accessible" || echo "❌ Milvus HTTP not accessible"
timeout 3 telnet localhost 8081 && echo "✅ RAG Server accessible" || echo "❌ RAG Server not accessible"
timeout 3 telnet localhost 8000 && echo "✅ NIM accessible" || echo "❌ NIM not accessible"

echo "🎉 Port-forward setup complete!"
