#!/usr/bin/env python3

from pymilvus import connections, utility, Collection

print('Connecting to Milvus...')
connections.connect('default', host='milvus', port='19530')
print('Connected successfully!')

print('Listing collections...')
collections = utility.list_collections()
print('Found', len(collections), 'collections:')
for col in collections:
    print('  -', col)

print('Checking hammerspace_docs collection...')
if 'hammerspace_docs' in collections:
    collection = Collection('hammerspace_docs')
    print('hammerspace_docs exists with', collection.num_entities, 'entities')
    
    # Check if collection is loaded
    if collection.has_index():
        print('Collection has index')
    else:
        print('Collection does not have index')
        
    # Try to load the collection
    try:
        collection.load()
        print('Collection loaded successfully')
        print('Collection now has', collection.num_entities, 'entities')
    except Exception as e:
        print('Error loading collection:', e)
else:
    print('hammerspace_docs collection not found!')

print('Check complete!')
