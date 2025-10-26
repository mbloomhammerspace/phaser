#!/bin/bash

echo "Setting up port forwards for Mac..."

# Attu (Milvus Admin UI)
echo "Setting up Attu (Milvus Admin UI) on localhost:3001..."
kubectl port-forward service/attu 3001:3001 &
ATTU_PID=$!

# RAG Playground Frontend
echo "Setting up RAG Playground Frontend on localhost:3000..."
kubectl port-forward service/clean-rag-frontend 3000:3000 &
RAG_FRONTEND_PID=$!

# Milvus Database
echo "Setting up Milvus Database on localhost:19530..."
kubectl port-forward service/milvus 19530:19530 &
MILVUS_PID=$!

# Milvus Metrics
echo "Setting up Milvus Metrics on localhost:9091..."
kubectl port-forward service/milvus 9091:9091 &
MILVUS_METRICS_PID=$!

# NIM LLM Service
echo "Setting up NIM LLM Service on localhost:8000..."
kubectl port-forward service/nim-llm 8000:8000 &
NIM_LLM_PID=$!

# NIM AIQ Service
echo "Setting up NIM AIQ Service on localhost:8001..."
kubectl port-forward service/nim-aiq 8001:8000 &
NIM_AIQ_PID=$!

# RAG Server
echo "Setting up RAG Server on localhost:8080..."
kubectl port-forward service/rag-server 8080:8080 &
RAG_SERVER_PID=$!

# RAG NV Ingest
echo "Setting up RAG NV Ingest on localhost:7670..."
kubectl port-forward service/rag-nv-ingest 7670:7670 &
RAG_INGEST_PID=$!

echo ""
echo "Port forwards established:"
echo "  - Attu (Milvus Admin UI): http://localhost:3001"
echo "  - RAG Playground Frontend: http://localhost:3000"
echo "  - Milvus Database: localhost:19530"
echo "  - Milvus Metrics: http://localhost:9091"
echo "  - NIM LLM Service: http://localhost:8000"
echo "  - NIM AIQ Service: http://localhost:8001"
echo "  - RAG Server: http://localhost:8080"
echo "  - RAG NV Ingest: http://localhost:7670"
echo ""
echo "Process IDs:"
echo "  - Attu: $ATTU_PID"
echo "  - RAG Frontend: $RAG_FRONTEND_PID"
echo "  - Milvus: $MILVUS_PID"
echo "  - Milvus Metrics: $MILVUS_METRICS_PID"
echo "  - NIM LLM: $NIM_LLM_PID"
echo "  - NIM AIQ: $NIM_AIQ_PID"
echo "  - RAG Server: $RAG_SERVER_PID"
echo "  - RAG Ingest: $RAG_INGEST_PID"
echo ""
echo "To stop all port forwards, run: kill $ATTU_PID $RAG_FRONTEND_PID $MILVUS_PID $MILVUS_METRICS_PID $NIM_LLM_PID $NIM_AIQ_PID $RAG_SERVER_PID $RAG_INGEST_PID"

# Save PIDs to file for later cleanup
echo "$ATTU_PID $RAG_FRONTEND_PID $MILVUS_PID $MILVUS_METRICS_PID $NIM_LLM_PID $NIM_AIQ_PID $RAG_SERVER_PID $RAG_INGEST_PID" > port_forward_pids.txt

