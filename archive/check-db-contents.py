from pymilvus import connections, Collection, utility
import sys

def connect_to_milvus():
    try:
        connections.connect('default', host='milvus', port='19530')
        print("Connected to Milvus")
        return True
    except Exception as e:
        print("Failed to connect to Milvus:", e)
        return False

def get_collection_details(collection_name):
    try:
        collection = Collection(collection_name)
        collection.load()
        print(f"  Schema fields: {[field.name for field in collection.schema.fields]}")
        return collection.num_entities
    except Exception as e:
        print(f"Error checking {collection_name}: {e}")
        return -1

def main():
    print("Connecting to Milvus...")
    if not connect_to_milvus():
        sys.exit(1)
    print("Connected successfully!")

    print("Listing all collections...")
    collections = utility.list_collections()
    print(f"Found {len(collections)} collections: {collections}")

    for col_name in collections:
        print(f"\n{col_name}:")
        num_entities = get_collection_details(col_name)
        if num_entities != -1:
            print(f"  {num_entities} entities")
            # Get sample documents to see what they contain
            if col_name == 'hammerspace_docs':
                try:
                    collection = Collection(col_name)
                    collection.load()
                    # Query first 5 documents to see their content
                    res = collection.query(
                        expr="pk > 0", 
                        output_fields=["pk", "source", "text"], 
                        limit=5
                    )
                    print("  Sample documents:")
                    for i, doc in enumerate(res):
                        print(f"    Doc {i+1}: source='{doc['source']}' text_preview='{doc['text'][:100]}...'")
                except Exception as e:
                    print(f"  Error querying sample docs: {e}")
        else:
            print("  Error retrieving entity count.")

if __name__ == "__main__":
    main()
