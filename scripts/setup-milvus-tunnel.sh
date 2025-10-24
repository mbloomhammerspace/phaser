#!/bin/bash

# Setup SSH tunnel to access Milvus from jumphost
# This script should be run on the jumphost (132.145.204.155)

echo "🔧 Setting up SSH tunnel to Milvus..."

# Kill any existing tunnels
pkill -f "ssh.*tunnel" || true
sleep 2

# Create SSH tunnel to access Milvus NodePort
# Tunnel: localhost:19530 -> K8s-node:30195 (Milvus GRPC)
# Tunnel: localhost:9091 -> K8s-node:30195 (Milvus HTTP)

echo "Creating SSH tunnel to Milvus..."
ssh -f -N -L 19530:10.0.0.25:30195 ubuntu@10.0.0.25 &
ssh -f -N -L 9091:10.0.0.25:30991 ubuntu@10.0.0.25 &

sleep 3

echo "Testing Milvus connectivity..."
timeout 3 telnet localhost 19530 && echo "✅ Milvus GRPC (19530) accessible" || echo "❌ Milvus GRPC (19530) not accessible"
timeout 3 telnet localhost 9091 && echo "✅ Milvus HTTP (9091) accessible" || echo "❌ Milvus HTTP (9091) not accessible"

echo "🎉 Milvus tunnel setup complete!"
echo "   - Milvus GRPC: localhost:19530"
echo "   - Milvus HTTP: localhost:9091"
