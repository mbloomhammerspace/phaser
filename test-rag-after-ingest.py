#!/usr/bin/env python3

import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

import requests
import json

RAG_URL = 'http://rag-server:8081'

print('=== Testing RAG Server After nv-ingest Document Upload ===')

# Test search endpoint to see if the ingested document is available
search_data = {
    "query": "test document",
    "collection_names": ["hammerspace_docs"],
    "vdb_top_k": 5,
    "reranker_top_k": 3
}

try:
    response = requests.post(f'{RAG_URL}/search', json=search_data, timeout=30)
    print(f'Search response: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Total results: {data.get("total_results", 0)}')
        print(f'Results count: {len(data.get("results", []))}')
        
        if data.get("results"):
            print('\nSearch Results:')
            for i, result in enumerate(data["results"]):
                print(f'\nResult {i+1}:')
                print(f'  Score: {result.get("score", "N/A")}')
                print(f'  Content: {result.get("content", "N/A")[:200]}...')
                print(f'  Source: {result.get("document_name", "N/A")}')
        else:
            print('No documents found in hammerspace_docs collection')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Search error: {e}')

print('\n=== Testing RAG Server Generate Endpoint ===')

# Test the generate endpoint to see if it can use the ingested document
generate_data = {
    "messages": [
        {"role": "user", "content": "What can you tell me about the test document?"}
    ],
    "collection_names": ["hammerspace_docs"],
    "use_knowledge_base": True,
    "temperature": 0.1,
    "max_tokens": 200
}

try:
    response = requests.post(f'{RAG_URL}/generate', json=generate_data, timeout=30)
    print(f'Generate response: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Generated response available: {bool(data)}')
        
        if data.get("choices"):
            choice = data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "No content")
            print(f'Generated content: {content}')
            
            # Check for citations
            if data.get("citations"):
                citations = data["citations"]
                print(f'Citations: {citations.get("total_results", 0)} sources')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Generate error: {e}')

print('\n=== RAG Server Test Complete ===')
