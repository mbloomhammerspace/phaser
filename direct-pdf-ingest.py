#!/usr/bin/env python3

import requests
import json
import os
from pathlib import Path

def ingest_pdf_directly():
    """Ingest PDF directly using the RAG Blueprint API"""
    
    # RAG server API endpoint
    RAG_API_URL = "http://rag-server:8081"
    
    # PDF file path
    PDF_PATH = "/mnt/iscsi/pdf-test/test-document.pdf"
    
    print("=== Direct PDF Ingestion to Milvus ===")
    
    # Check if PDF exists
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF not found: {PDF_PATH}")
        return False
    
    print(f"✅ Found PDF: {PDF_PATH}")
    
    # Test RAG server connection
    try:
        response = requests.get(f"{RAG_API_URL}/health", timeout=5)
        print(f"✅ RAG server health: {response.status_code}")
    except Exception as e:
        print(f"❌ RAG server connection failed: {e}")
        return False
    
    # Try to create a collection first
    collection_data = {
        "name": "test_documents",
        "description": "Test collection for PDF ingestion",
        "embedding_model": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "chunk_size": 512,
        "chunk_overlap": 50
    }
    
    try:
        print("Creating collection...")
        response = requests.post(f"{RAG_API_URL}/collections", json=collection_data, timeout=10)
        print(f"Collection creation: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Collection creation error: {e}")
    
    # Upload PDF
    try:
        print("Uploading PDF...")
        with open(PDF_PATH, 'rb') as f:
            files = {'file': ('test-document.pdf', f, 'application/pdf')}
            data = {
                'collection_name': 'test_documents',
                'chunk_size': 512,
                'chunk_overlap': 50
            }
            
            response = requests.post(f"{RAG_API_URL}/upload", files=files, data=data, timeout=60)
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
    success = ingest_pdf_directly()
    if success:
        print("\n=== Ingestion Complete ===")
    else:
        print("\n=== Ingestion Failed ===")
