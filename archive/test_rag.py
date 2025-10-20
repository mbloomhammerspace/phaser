#!/usr/bin/env python3

import requests
import json

RAG_URL = 'http://rag-server:8081'

print('=== Testing RAG Pipeline with Ingested PDFs ===')

print('Testing search endpoint...')
search_payload = {
    'query': 'What is discussed in the documents?',
    'collection_names': ['hammerspace_docs']
}

try:
    search_response = requests.post(f'{RAG_URL}/search', json=search_payload, timeout=60)
    print('Search response:', search_response.status_code)
    if search_response.status_code == 200:
        results = search_response.json()
        print('Search results:')
        print(json.dumps(results, indent=2))
    else:
        print('Search error:', search_response.text)
except Exception as e:
    print('Search exception:', e)

print()
print('Testing generate endpoint...')
generate_payload = {
    'messages': [
        {'role': 'user', 'content': 'Summarize the content of the ingested documents.'}
    ],
    'collection_names': ['hammerspace_docs']
}

try:
    generate_response = requests.post(f'{RAG_URL}/generate', json=generate_payload, timeout=120)
    print('Generate response:', generate_response.status_code)
    if generate_response.status_code == 200:
        results = generate_response.json()
        print('Generate results:')
        print(json.dumps(results, indent=2))
    else:
        print('Generate error:', generate_response.text)
except Exception as e:
    print('Generate exception:', e)

print()
print('Testing collections endpoint...')
try:
    collections_response = requests.get(f'{RAG_URL}/collections', timeout=10)
    print('Collections response:', collections_response.status_code)
    if collections_response.status_code == 200:
        collections = collections_response.json()
        print('Available collections:')
        for col in collections:
            print('  -', col)
    else:
        print('Collections error:', collections_response.text)
except Exception as e:
    print('Collections exception:', e)

print()
print('=== RAG Pipeline Test Complete ===')
