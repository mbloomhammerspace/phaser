#!/usr/bin/env python3
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Connect to Milvus
connections.connect('default', host='milvus', port='19530')
print('Connected to Milvus')

# Create a test collection
collection_name = 'test_documents'
print(f'Creating collection: {collection_name}')

fields = [
    FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name='text', dtype=DataType.VARCHAR, max_length=512)
]
schema = CollectionSchema(fields, description='Test documents collection')
collection = Collection(name=collection_name, schema=schema)

# Create index
index_params = {
    'metric_type': 'L2',
    'index_type': 'IVF_FLAT',
    'params': {'nlist': 128}
}
collection.create_index(field_name='embedding', index_params=index_params)
print('Index created')

# Insert test documents
test_docs = [
    'This is a test document about artificial intelligence.',
    'The NVIDIA RAG Blueprint provides advanced capabilities.',
    'Vector databases enable semantic search and retrieval.',
    'GPU acceleration improves embedding performance.',
    'Document processing is key to RAG systems.'
]

# Generate random embeddings
embeddings = [np.random.rand(1536).tolist() for _ in test_docs]

# Insert data
data = [embeddings, test_docs]
collection.insert(data)
collection.flush()

print(f'Inserted {len(test_docs)} documents')
print(f'Collection now contains {collection.num_entities} entities')
print('✓ Test embeddings created successfully!')
