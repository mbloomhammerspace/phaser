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

print("\n=== Embedding Test Complete ===")
