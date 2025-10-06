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

def create_all_pdfs_collection():
    collection_name = 'all_pdfs'
    
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
    schema = CollectionSchema(fields, description="All PDFs collection for RAG Blueprint")
    
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

def ingest_pdf(pdf_path, collection, batch_size=100):
    filename = os.path.basename(pdf_path)
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return False
    
        # Truncate text to fit Milvus VARCHAR max_length (leaving buffer)
        text = text[:3500]
    embedding = generate_simple_embedding(text)
    
    data = [
        [embedding],
        [filename],
        [text]
    ]
    
    try:
        collection.insert(data)
        return True
    except Exception as e:
        print(f"Failed to ingest {filename}: {e}")
        return False

def main():
    print("=== Ingesting All Available PDFs ===")
    
    if not connect_to_milvus():
        return
    
    collection = create_all_pdfs_collection()
    
    # Process both directories
    pdf_dirs = ["/data/pdf-test", "/data/pdfs"]
    total_processed = 0
    total_successful = 0
    batch_count = 0
    
    for pdf_dir in pdf_dirs:
        if not os.path.exists(pdf_dir):
            print(f"Directory not found: {pdf_dir}")
            continue
            
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        print(f"Processing {len(pdf_files)} PDFs from {pdf_dir}")
        
        for i, pdf_file in enumerate(pdf_files):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            if ingest_pdf(pdf_path, collection):
                total_successful += 1
            total_processed += 1
            
            # Flush every 100 documents
            if total_processed % 100 == 0:
                collection.flush()
                print(f"Processed {total_processed} files, {total_successful} successful")
    
    # Final flush
    collection.flush()
    collection.load()
    
    print("=== Final Ingestion Summary ===")
    print("Total processed:", total_processed, "files")
    print("Total successful:", total_successful, "files")
    print("Collection entities:", collection.num_entities)

if __name__ == "__main__":
    main()
