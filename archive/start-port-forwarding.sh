#!/bin/bash

# Port Forwarding Manager for NVIDIA RAG System
# Usage: ./start-port-forwarding.sh

echo "🔌 Starting Port Forwarding for NVIDIA RAG System"
echo "=================================================="
echo ""

# Kill any existing port forwards
echo "🧹 Cleaning up existing port forwards..."
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 2

# Start port forwarding for each service
echo "🚀 Starting port forwards..."

# RAG Playground (with MCP toggle)
echo "   📱 RAG Playground (MCP) -> localhost:30082"
kubectl port-forward svc/nvidia-rag-playground-mcp 30082:3000 >/dev/null 2>&1 &

# Milvus
echo "   🗄️  Milvus -> localhost:19530"
kubectl port-forward svc/milvus 19530:19530 >/dev/null 2>&1 &

# RAG Server
echo "   🤖 RAG Server -> localhost:8081"
kubectl port-forward svc/rag-server 8081:8081 >/dev/null 2>&1 &

# Ingestor Server
echo "   📥 Ingestor Server -> localhost:8082"
kubectl port-forward svc/ingestor-server 8082:8082 >/dev/null 2>&1 &

# Triton genai-perf (if deployed)
echo "   🧪 Triton genai-perf -> localhost:8000"
kubectl port-forward svc/triton-genai-perf-service 8000:8000 >/dev/null 2>&1 &

sleep 3

echo ""
echo "✅ Port forwarding active!"
echo "=================================================="
echo ""
echo "📋 Access Points (localhost only):"
echo "   🎮 RAG Playground (with MCP toggle): http://localhost:30082"
echo "   🗄️  Milvus Database:                 localhost:19530"
echo "   🤖 RAG Server API:                   http://localhost:8081"
echo "   📥 Ingestor API:                     http://localhost:8082"
echo "   🧪 Triton genai-perf:                http://localhost:8000"
echo ""
echo "🔒 All services are now accessible via localhost (NAT)"
echo "🛑 To stop port forwarding: pkill -f 'kubectl port-forward'"
echo ""
echo "📊 Monitoring port forwards..."
echo "   Press Ctrl+C to stop all forwards"
echo ""

# Keep script running and monitor
wait
