#!/usr/bin/env python3

import requests
import json

PLAYGROUND_URL = "http://rag-playground-registry-service:8080"
print("Testing Enhanced RAG Playground with MCP Integration...")

# Test stats endpoint
try:
    response = requests.get(f"{PLAYGROUND_URL}/stats", timeout=10)
    print(f"Stats: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Status: {stats.get('status')}")
        print(f"Collection: {stats.get('collection_name')}")
        print(f"MCP URL: {stats.get('mcp_wrapper_url', 'N/A')}")
except Exception as e:
    print(f"Stats error: {e}")

# Test search endpoint
try:
    search_payload = {"query": "HammerSpace", "top_k": 2}
    response = requests.post(f"{PLAYGROUND_URL}/search", json=search_payload, timeout=30)
    print(f"Search: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        method = result.get("method", "unknown")
        results_count = len(result.get("results", []))
        print(f"Search method: {method}")
        print(f"Results count: {results_count}")
        if result.get("results"):
            first_result = result["results"][0]
            print(f"First result source: {first_result.get('source', 'unknown')}")
    else:
        print(f"Search failed: {response.text}")
except Exception as e:
    print(f"Search error: {e}")

print("Integration test completed.")
