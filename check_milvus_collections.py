#!/usr/bin/env python3

import sys
import subprocess

# Install pymilvus
subprocess.check_call([sys.executable, "-m", "pip", "install", "pymilvus"])

from pymilvus import connections, utility, Collection

print("=== Checking Milvus Collections ===")

# Try connecting to different Milvus instances
milvus_services = [
    ("milvus", "milvus", 19530),
    ("milvus-external", "milvus-external", 19530),
    ("milvus-standalone", "milvus-standalone", 19530),
]

for service_name, host, port in milvus_services:
    print(f"\n--- Checking {service_name} ---")
    try:
        connections.connect('default', host=host, port=port)
        print(f"Connected to {service_name}")
        
        collections = utility.list_collections()
        print(f"Collections in {service_name}: {collections}")
        
        if 'hammerspace_docs' in collections:
            collection = Collection('hammerspace_docs')
            print(f"hammerspace_docs exists with {collection.num_entities} entities")
            
            # Check schema
            schema = collection.schema
            print("Schema:")
            for field in schema.fields:
                print(f"  - {field.name}: {field.dtype}")
                if hasattr(field, 'params') and 'dim' in field.params:
                    print(f"    dim: {field.params['dim']}")
        else:
            print("hammerspace_docs collection not found")
            
    except Exception as e:
        print(f"Failed to connect to {service_name}: {e}")

print("\n=== Check Complete ===")
