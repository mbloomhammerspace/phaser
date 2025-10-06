from pymilvus import connections, Collection, utility

def main():
    print("Connecting to Milvus...")
    connections.connect('default', host='milvus', port='19530')
    print("Connected successfully!")
    
    print("Listing all collections...")
    collections = utility.list_collections()
    print(f"Found {len(collections)} collections: {collections}")
    
    for col_name in collections:
        try:
            col = Collection(col_name)
            col.load()
            print(f"{col_name}: {col.num_entities} entities")
            
            # Get schema info
            schema = col.schema
            print(f"  Schema fields: {[field.name for field in schema.fields]}")
            
            # Sample some data if available
            if col.num_entities > 0:
                results = col.query(expr="pk > 0", output_fields=["source"], limit=3)
                print(f"  Sample sources: {[r.get('source', 'N/A') for r in results]}")
            else:
                print("  No entities found")
            print()
        except Exception as e:
            print(f"Error checking {col_name}: {e}")

if __name__ == "__main__":
    main()
