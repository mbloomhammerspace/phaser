#!/usr/bin/env python3

import requests
import json

RAG_URL = "http://rag-server-mcp-enhanced:8081"
print("Testing Enhanced RAG Server with MCP...")

# Test health endpoint
try:
    response = requests.get(f"{RAG_URL}/health", timeout=10)
    print(f"Health: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        message = health.get("message")
        print(f"Message: {message}")
        mcp_status = health.get("mcp_status", {})
        print(f"MCP Status: {mcp_status}")
except Exception as e:
    print(f"Health error: {e}")

# Test MCP status endpoint
try:
    response = requests.get(f"{RAG_URL}/mcp/status", timeout=10)
    print(f"MCP Status: {response.status_code}")
    if response.status_code == 200:
        mcp_status = response.json()
        print(f"MCP Status data: {mcp_status}")
except Exception as e:
    print(f"MCP Status error: {e}")

# Test search endpoint
try:
    search_payload = {
        "query": "HammerSpace",
        "collection_names": ["hammerspace_docs"],
        "vdb_top_k": 3
    }
    response = requests.post(f"{RAG_URL}/search", json=search_payload, timeout=30)
    print(f"Search: {response.status_code}")
    if response.status_code == 200:
        search_result = response.json()
        total_results = search_result.get("total_results", 0)
        print(f"Search results: {total_results} documents found")
        if search_result.get("results"):
            first_result = search_result["results"][0]
            doc_name = first_result.get("document_name", "Unknown")
            score = first_result.get("score", 0.0)
            print(f"First result: {doc_name} (score: {score:.3f})")
    else:
        print(f"Search failed: {response.text}")
except Exception as e:
    print(f"Search error: {e}")

print("Test completed.")
