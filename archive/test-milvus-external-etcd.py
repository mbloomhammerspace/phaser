#!/usr/bin/env python3
import requests
import time

# Test the new Milvus with external etcd
MILVUS_HOST = "milvus-external-etcd-clean"
MILVUS_HTTP_PORT = 9091
MILVUS_GRPC_PORT = 19530

print("=== Testing Milvus with External etcd ===")
print(f"Host: {MILVUS_HOST}")
print(f"HTTP Port: {MILVUS_HTTP_PORT}")
print(f"gRPC Port: {MILVUS_GRPC_PORT}")

# Test HTTP health endpoint
try:
    response = requests.get(f"http://{MILVUS_HOST}:{MILVUS_HTTP_PORT}/healthz", timeout=10)
    response.raise_for_status()
    print(f"✓ HTTP health check successful: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"✗ HTTP health check failed: {e}")

# Test HTTP API
try:
    response = requests.get(f"http://{MILVUS_HOST}:{MILVUS_HTTP_PORT}/health", timeout=10)
    response.raise_for_status()
    print(f"✓ HTTP API health check successful: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"✗ HTTP API health check failed: {e}")

# Test collections endpoint
try:
    response = requests.get(f"http://{MILVUS_HOST}:{MILVUS_HTTP_PORT}/collections", timeout=10)
    response.raise_for_status()
    print(f"✓ Collections endpoint accessible: {response.status_code}")
    print(f"Collections: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"✗ Collections endpoint failed: {e}")

print("\n=== Milvus External etcd Test Complete ===")
