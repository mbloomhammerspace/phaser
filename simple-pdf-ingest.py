#!/usr/bin/env python3

import requests
import os
import time
from pathlib import Path

def ingest_pdf_simple():
    """Simple PDF ingestion using RAG Blueprint API"""
    
    print("=== Simple PDF Ingestion ===")
    
    # RAG server endpoint
    RAG_URL = "http://rag-server:8081"
    
    # Check PDF directory
    pdf_dir = Path("/mnt/iscsi/pdf-test")
    if not pdf_dir.exists():
        print(f"❌ PDF directory {pdf_dir} not found")
        return False
    
    pdfs = list(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"❌ No PDF files found in {pdf_dir}")
        return False
    
    print(f"✅ Found {len(pdfs)} PDF files:")
    for pdf in pdfs:
        print(f"  - {pdf.name}")
    
    # Test RAG server connection
    try:
        response = requests.get(f"{RAG_URL}/health", timeout=5)
        print(f"✅ RAG server health: {response.status_code}")
    except Exception as e:
        print(f"❌ RAG server connection failed: {e}")
        return False
    
    # Try to create a collection first
    collection_data = {
        "name": "test_documents",
        "description": "Test collection for PDF ingestion",
        "embedding_model": "nvidia/llama-3.3-nemotron-super-49b-v1"
    }
    
    try:
        print("Creating collection...")
        response = requests.post(f"{RAG_URL}/collections", json=collection_data, timeout=10)
        print(f"Collection creation: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Collection creation error: {e}")
    
    # Try to upload a PDF
    pdf_file = pdfs[0]  # Use the first PDF
    print(f"Uploading PDF: {pdf_file.name}")
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            data = {
                'collection_name': 'test_documents',
                'chunk_size': 512,
                'chunk_overlap': 50
            }
            
            response = requests.post(f"{RAG_URL}/upload", files=files, data=data, timeout=60)
            print(f"PDF upload: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ PDF ingestion successful!")
                return True
            else:
                print("❌ PDF ingestion failed")
                return False
                
    except Exception as e:
        print(f"❌ PDF upload error: {e}")
        return False

if __name__ == "__main__":
    success = ingest_pdf_simple()
    if success:
        print("\n=== SUCCESS ===")
        print("PDF ingestion completed!")
    else:
        print("\n=== FAILED ===")
        print("PDF ingestion failed")