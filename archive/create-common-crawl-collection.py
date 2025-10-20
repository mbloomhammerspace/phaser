import os
import sys
import fitz
import json
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import numpy as np

def connect_to_milvus():
    try:
        connections.connect('default', host='milvus', port='19530')
        print("Connected to Milvus")
        return True
    except Exception as e:
        print("Failed to connect to Milvus:", e)
        return False

def create_common_crawl_collection():
    collection_name = 'common_crawl'
    
    # Drop existing collection if it exists
    if utility.has_collection(collection_name):
        print(f"Dropping existing collection: {collection_name}")
        utility.drop_collection(collection_name)
    
    print(f"Creating new collection: {collection_name}")
    fields = [
        FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=2048),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
    ]
    schema = CollectionSchema(fields, description="Common Crawl documents for RAG Blueprint")
    
    collection = Collection(name=collection_name, schema=schema)
    
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    print("Created collection and index")
    
    return collection

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print("Error extracting text from", pdf_path, ":", e)
        return None

def generate_simple_embedding(text):
    # In a real scenario, this would call an embedding model
    return np.random.rand(2048).tolist()

def ingest_pdf(pdf_path, collection):
    filename = os.path.basename(pdf_path)
    print("Processing:", filename)
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text found in:", filename)
        return False
    
    # Truncate text to fit Milvus VARCHAR max_length (leaving buffer)
    text = text[:3950]
    embedding = generate_simple_embedding(text)
    
    data = [
        [embedding],
        [filename],
        [text]
    ]
    
    try:
        collection.insert(data)
        collection.flush()
        print("Successfully ingested:", filename)
        return True
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")
        return False

def main():
    print("=== Creating Common Crawl Collection and Ingesting HammerSpace PDFs ===")
    
    if not connect_to_milvus():
        return
    
    collection = create_common_crawl_collection()
    collection.load()
    
    pdf_dir = "/data/pdf-test"
    if not os.path.exists(pdf_dir):
        print("PDF directory not found:", pdf_dir)
        return
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} HammerSpace PDF files in {pdf_dir}")
    
    processed = 0
    successful = 0
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        if ingest_pdf(pdf_path, collection):
            successful += 1
        processed += 1
    
    print("=== Ingestion Summary ===")
    print("Processed:", processed, "files")
    print("Successful:", successful, "files")
    print("Total documents in collection:", collection.num_entities)
    
    # Verify the documents are correct
    print("\n=== Verifying Ingested Documents ===")
    try:
        res = collection.query(
            expr="pk > 0", 
            output_fields=["pk", "source", "text"], 
            limit=5
        )
        print("Sample documents:")
        for i, doc in enumerate(res):
            print(f"  Doc {i+1}: source='{doc['source']}' text_preview='{doc['text'][:100]}...'")
    except Exception as e:
        print(f"Error verifying documents: {e}")

if __name__ == "__main__":
    main()
