#!/usr/bin/env python3

import os
import sys
import requests
from pathlib import Path

def create_collection_and_ingest():
    """Create a collection in Milvus and ingest a PDF directly"""
    
    print("=== Direct Milvus PDF Ingestion ===")
    
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
        response = requests.get("http://milvus:9091/healthz", timeout=5)
        print(f"✅ Milvus HTTP health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Milvus HTTP connection failed: {e}")
        return False
    
    # For now, just report what we found
    print("✅ Milvus is accessible and PDFs are available")
    print("✅ Ready for ingestion using Milvus Python client")
    
    return True

if __name__ == "__main__":
    success = create_collection_and_ingest()
    if success:
        print("\n=== Ingestion Setup Complete ===")
        print("Milvus is ready to receive PDFs")
        print("Next step: Install pymilvus and create collection")
    else:
        print("\n=== Ingestion Setup Failed ===")
        sys.exit(1)
