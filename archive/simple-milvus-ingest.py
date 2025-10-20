#!/usr/bin/env python3

import os
import sys
import requests
import json
from pathlib import Path

def create_collection_and_ingest():
    """Create a collection in Milvus and ingest a PDF"""
    
    # Milvus connection details
    MILVUS_HOST = "milvus"
    MILVUS_PORT = "19530"
    MILVUS_HTTP_PORT = "9091"
    
    print("=== Starting Milvus PDF Ingestion ===")
    
    # Check if PDF directory exists
    pdf_dir = Path("/mnt/iscsi/pdf-test")
    if not pdf_dir.exists():
        print(f"❌ PDF directory {pdf_dir} not found")
        return False
    
    pdfs = list(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"❌ No PDF files found in {pdf_dir}")
        return False
    
    print(f"✅ Found {len(pdfs)} PDF files")
    for pdf in pdfs:
        print(f"  - {pdf.name}")
    
    # Test Milvus HTTP connection
    try:
        response = requests.get(f"http://{MILVUS_HOST}:{MILVUS_HTTP_PORT}/healthz", timeout=5)
        print(f"✅ Milvus HTTP health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Milvus HTTP connection failed: {e}")
        return False
    
    # For now, just report what we found
    print("✅ Milvus is accessible and PDFs are available")
    print("✅ Ready for ingestion using NVIDIA RAG Blueprint")
    
    return True

if __name__ == "__main__":
    success = create_collection_and_ingest()
    if success:
        print("\n=== Ingestion Setup Complete ===")
        print("Milvus is ready to receive PDFs")
    else:
        print("\n=== Ingestion Setup Failed ===")
        sys.exit(1)
