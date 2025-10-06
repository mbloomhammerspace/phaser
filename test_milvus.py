#!/usr/bin/env python3
import requests
import json

# Test Milvus HTTP endpoints
milvus_url = "http://150.136.235.189:30002"

def test_milvus_endpoints():
    print("Testing Milvus HTTP endpoints...")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{milvus_url}/healthz", timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test collections endpoint
    try:
        response = requests.get(f"{milvus_url}/collections", timeout=5)
        print(f"Collections: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Collections failed: {e}")
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{milvus_url}/metrics", timeout=5)
        print(f"Metrics: {response.status_code} - {response.text[:200]}...")
    except Exception as e:
        print(f"Metrics failed: {e}")

if __name__ == "__main__":
    test_milvus_endpoints()
