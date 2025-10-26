#!/bin/bash

# =============================================================================
# Quick NAT Sessions Setup - NVIDIA RAG Blueprint
# =============================================================================
# Simple script to establish all NAT port forwarding sessions
# =============================================================================

echo "🚀 Establishing NVIDIA RAG Blueprint NAT sessions..."

# Kill existing port forwards
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 2

# Core RAG Services
echo "📡 Starting RAG Playground (3000)..."
kubectl port-forward service/clean-rag-frontend 3000:3000 --address=0.0.0.0 &

echo "📡 Starting RAG Server API (8081)..."
kubectl port-forward service/rag-server 8081:8081 --address=0.0.0.0 &

echo "📡 Starting RAG Ingestor (8082)..."
kubectl port-forward service/ingestor-server 8082:8082 --address=0.0.0.0 &

# AI-Q Research Assistant
echo "📡 Starting AI-Q Frontend (8051)..."
kubectl port-forward service/aiq-aira-frontend 8051:3000 --address=0.0.0.0 &

echo "📡 Starting AI-Q Backend (3838)..."
kubectl port-forward service/aiq-aira-backend 3838:3838 --address=0.0.0.0 &

echo "📡 Starting AI-Q Nginx (8052)..."
kubectl port-forward service/aiq-aira-nginx 8052:8051 --address=0.0.0.0 &

echo "📡 Starting Phoenix Service (6006)..."
kubectl port-forward service/aiq-phoenix 6006:6006 --address=0.0.0.0 &

echo "📡 Starting AI-Q LLM (8000)..."
kubectl port-forward service/aira-instruct-llm 8000:8000 --address=0.0.0.0 &

# Vector Database & Management
echo "📡 Starting Milvus Database (19530)..."
kubectl port-forward service/milvus 19530:19530 --address=0.0.0.0 &

echo "📡 Starting Milvus Metrics (9091)..."
kubectl port-forward service/milvus 9091:9091 --address=0.0.0.0 &

echo "📡 Starting Attu UI (3001)..."
kubectl port-forward service/attu 3001:3000 --address=0.0.0.0 &

# Observability & Monitoring
echo "📡 Starting Jaeger Tracing (16686)..."
kubectl port-forward service/jaeger-query 16686:16686 --address=0.0.0.0 &

echo "📡 Starting Zipkin Tracing (9411)..."
kubectl port-forward service/zipkin 9411:9411 --address=0.0.0.0 &

echo "📡 Starting Grafana Dashboard (30671)..."
kubectl port-forward service/grafana 30671:3000 --address=0.0.0.0 &

# NeMo Retriever Services
echo "📡 Starting NeMo Embedding (8001)..."
kubectl port-forward service/nemoretriever-embedding-ms 8001:8000 --address=0.0.0.0 &

echo "📡 Starting NeMo Reranking (8002)..."
kubectl port-forward service/nemoretriever-reranking-ms 8002:8000 --address=0.0.0.0 &

# Data & Cache Services
echo "📡 Starting Redis Cache (6379)..."
kubectl port-forward service/rag-redis-master 6379:6379 --address=0.0.0.0 &

echo "📡 Starting etcd Database (2379)..."
kubectl port-forward service/etcd 2379:2379 --address=0.0.0.0 &

echo ""
echo "✅ All NAT sessions established!"
echo ""
echo "🌐 Access URLs:"
echo "  http://localhost:3000  - RAG Playground"
echo "  http://localhost:3001  - Attu UI (Milvus)"
echo "  http://localhost:8081  - RAG Server API"
echo "  http://localhost:8082  - RAG Ingestor API"
echo "  http://localhost:8051  - AI-Q Research Assistant"
echo "  http://localhost:16686 - Jaeger Tracing"
echo "  http://localhost:9411  - Zipkin Tracing"
echo "  http://localhost:30671 - Grafana Dashboard"
echo ""
echo "📊 Check status: ps aux | grep 'kubectl port-forward'"
echo "🛑 Stop all: pkill -f 'kubectl port-forward'"
