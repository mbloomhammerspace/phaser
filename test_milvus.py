from pymilvus import connections, utility, Collection

try:
    print("Connecting to Milvus...")
    connections.connect('default', host='10.233.53.224', port=19530)
    print("✅ Milvus connection successful!")
    
    print("\nListing collections...")
    collections = utility.list_collections()
    print(f"Found {len(collections)} collections:")
    for i, name in enumerate(collections, 1):
        print(f"  {i}. {name}")
    
    if collections:
        print("\nGetting collection details...")
        for collection_name in collections[:5]:  # Show first 5 collections
            try:
                collection = Collection(collection_name)
                print(f"\nCollection: {collection_name}")
                print(f"  - Description: {collection.description}")
                print(f"  - Entities: {collection.num_entities}")
                print(f"  - Schema fields: {len(collection.schema.fields)}")
            except Exception as e:
                print(f"  - Error getting details for {collection_name}: {e}")
    else:
        print("No collections found")
        
except Exception as e:
    print(f"❌ Milvus connection failed: {e}")
