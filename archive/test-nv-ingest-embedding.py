#!/usr/bin/env python3

import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

import requests
import json

NV_INGEST_URL = 'http://nv-ingest-simple-api:8080'

print('=== Testing nv-ingest for Embedding Functionality ===')

# Test if nv-ingest has embedding endpoints
embedding_endpoints = ['/embed', '/embedding', '/embeddings', '/api/embed', '/api/embeddings', '/v1/embeddings']

for endpoint in embedding_endpoints:
    try:
        response = requests.post(f'{NV_INGEST_URL}{endpoint}', 
                               json={"text": "This is a test sentence for embedding."}, 
                               timeout=10)
        print(f'POST {endpoint}: {response.status_code}')
        if response.status_code in [200, 201]:
            print(f'  Success! Response: {response.json()}')
        elif response.status_code == 404:
            print(f'  Not found')
        else:
            print(f'  Error: {response.text[:100]}...')
    except Exception as e:
        print(f'POST {endpoint}: Error - {e}')

# Test if we can use the documents endpoint to get embeddings
print("\n=== Testing Documents Endpoint for Embedding ===")
try:
    # Try to upload a simple text and see if we get embeddings back
    files = {
        'documents': ('test.txt', 'This is a test document for embedding extraction.', 'text/plain')
    }
    data = {
        'collection_name': 'test_embedding'
    }
    response = requests.post(f'{NV_INGEST_URL}/documents', 
                           files=files, 
                           data=data, 
                           timeout=30)
    print(f'POST /documents: {response.status_code}')
    if response.status_code in [200, 201]:
        print(f'  Success! Response: {response.json()}')
    else:
        print(f'  Error: {response.text[:200]}...')
except Exception as e:
    print(f'POST /documents: Error - {e}')

print("\n=== Embedding Test Complete ===")
