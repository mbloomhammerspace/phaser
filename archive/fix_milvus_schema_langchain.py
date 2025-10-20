#!/usr/bin/env python3

import sys
import subprocess

# Install required packages
subprocess.check_call([sys.executable, "-m", "pip", "install", "pymilvus"])

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import numpy as np

print("=== Fixing Milvus Schema for LangChain Compatibility ===")

# Connect to Milvus
connections.connect('default', host='milvus', port='19530')
print("Connected to Milvus")

# Check current collection
if utility.has_collection('hammerspace_docs'):
    old_collection = Collection('hammerspace_docs')
    print(f"Current hammerspace_docs has {old_collection.num_entities} entities")
    
    # Get existing data
    old_collection.load()
    entities = old_collection.num_entities
    
    # Read all data from old collection
    data = []
    if entities > 0:
        # Query all data
        results = old_collection.query(expr="pk >= 0", output_fields=["pk", "vector", "source", "content"])
        print(f"Retrieved {len(results)} entities from old collection")
        data = results
    
    # Drop old collection
    utility.drop_collection('hammerspace_docs')
    print("Dropped old collection")

# Create new collection with LangChain-compatible schema
print("Creating new collection with LangChain-compatible schema...")

# LangChain Milvus expects these field names:
fields = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=2048),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),  # Changed back to 'text' for LangChain
]

schema = CollectionSchema(fields, description="RAG Blueprint documents with LangChain-compatible schema")
new_collection = Collection(name="hammerspace_docs", schema=schema)

# Create index
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
new_collection.create_index(field_name="vector", index_params=index_params)
print("Created collection and index")

# Load collection
new_collection.load()
print("Collection loaded")

# Insert data back if we had any
if data:
    print(f"Reinserting {len(data)} entities...")
    vectors = [item['vector'] for item in data]
    sources = [item['source'] for item in data]
    texts = [item['content'] for item in data]  # Map 'content' to 'text'
    
    insert_data = [
        vectors,
        sources,
        texts
    ]
    
    new_collection.insert(insert_data)
    new_collection.flush()
    print(f"Successfully reinserted {len(data)} entities")

print(f"Final collection has {new_collection.num_entities} entities")
print("=== Schema Fix Complete ===")
