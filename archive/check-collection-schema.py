from pymilvus import connections, Collection, utility

def main():
    print("Connecting to Milvus...")
    connections.connect('default', host='milvus', port='19530')
    print("Connected successfully!")

    if utility.has_collection('hammerspace_docs'):
        collection = Collection('hammerspace_docs')
        print("hammerspace_docs collection exists with", collection.num_entities, "entities")
        
        # Check collection schema
        schema = collection.schema
        print("Collection schema:")
        for i, field in enumerate(schema.fields):
            print(f"  {i}: {field.name} - {field.dtype}")
    else:
        print("hammerspace_docs collection not found!")

if __name__ == "__main__":
    main()
