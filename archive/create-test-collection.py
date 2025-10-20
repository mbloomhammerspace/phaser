#!/usr/bin/env python3
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Connect to the new Milvus with external etcd
MILVUS_HOST = "milvus-external-etcd-clean"
MILVUS_PORT = "19530"
COLLECTION_NAME = "test_collection"

print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")

try:
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    print("✓ Milvus connection successful")

    # Check if collection exists
    from pymilvus import list_collections
    collections = list_collections()
    print(f"Existing collections: {collections}")

    # Create a test collection if it doesn't exist
    if COLLECTION_NAME not in collections:
        print(f"Creating collection {COLLECTION_NAME}...")
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=256)
        ]
        schema = CollectionSchema(fields, description="Test collection for RAG Blueprint")
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        
        # Create an index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        print(f"✓ Collection {COLLECTION_NAME} created with index")
    else:
        print(f"Collection {COLLECTION_NAME} already exists")

    # List collections again
    collections = list_collections()
    print(f"Final collections: {collections}")

except Exception as e:
    print(f"✗ Error: {e}")
