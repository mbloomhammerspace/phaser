from pymilvus import connections, utility
import sys

milvus_services = [
    ('milvus', 19530),
    ('milvus-external-etcd-clean', 19530),
    ('milvus-standalone-working', 19530)
]

for service, port in milvus_services:
    try:
        print(f'Testing {service}:{port}...')
        connections.connect('default', host=service, port=port)
        collections = utility.list_collections()
        print(f'  Collections: {collections}')
        
        # Check hammerspace_docs if it exists
        if 'hammerspace_docs' in collections:
            from pymilvus import Collection
            col = Collection('hammerspace_docs')
            col.load()
            print(f'  hammerspace_docs: {col.num_entities} entities')
        
        connections.disconnect('default')
        print()
    except Exception as e:
        print(f'  Error: {e}')
        try:
            connections.disconnect('default')
        except:
            pass
        print()
