#!/usr/bin/env python3

import os
import time
from pathlib import Path

def wait_for_milvus():
    """Wait for Milvus to be ready"""
    print("Waiting for Milvus to be ready...")
    
    # Check if we can import pymilvus
    try:
        from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
        print("✅ pymilvus imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pymilvus: {e}")
        return False
    
    # Try to connect to Milvus
    max_retries = 30
    for i in range(max_retries):
        try:
            connections.connect("default", host="milvus", port="19530")
            print("✅ Connected to Milvus")
            
            # Check if Milvus is ready
            if utility.get_server_version():
                print("✅ Milvus is ready")
                return True
                
        except Exception as e:
            print(f"⏳ Attempt {i+1}/{max_retries}: Milvus not ready yet: {e}")
            time.sleep(10)
    
    print("❌ Milvus failed to become ready after 5 minutes")
    return False

def create_collection_and_ingest():
    """Create a collection and ingest a PDF"""
    
    if not wait_for_milvus():
        return False
    
    try:
        from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
        
        # Connect to Milvus
        connections.connect("default", host="milvus", port="19530")
        
        # Create collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
        ]
        
        schema = CollectionSchema(fields, "Test collection for PDF ingestion")
        collection_name = "test_documents"
        
        # Check if collection exists
        if utility.has_collection(collection_name):
            print(f"Collection {collection_name} already exists")
        else:
            # Create collection
            collection = Collection(collection_name, schema)
            print(f"✅ Created collection: {collection_name}")
        
        # Check PDF directory
        pdf_dir = Path("/mnt/iscsi/pdf-test")
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob("*.pdf"))
            print(f"✅ Found {len(pdfs)} PDF files")
            for pdf in pdfs:
                print(f"  - {pdf.name}")
        else:
            print(f"❌ PDF directory {pdf_dir} not found")
            return False
        
        print("✅ Collection created and ready for PDF ingestion")
        print("✅ Milvus is working and accessible")
        return True
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False

if __name__ == "__main__":
    success = create_collection_and_ingest()
    if success:
        print("\n=== SUCCESS ===")
        print("Milvus is ready for PDF ingestion!")
        print("You can now use the NVIDIA RAG Blueprint to ingest PDFs")
    else:
        print("\n=== FAILED ===")
        print("Milvus is not ready or there was an error")
