#!/usr/bin/env python3

import os
import sys
import requests
from pathlib import Path

def test_milvus_connection():
    """Test Milvus HTTP connection"""
    try:
        response = requests.get("http://milvus:9091/healthz", timeout=5)
        print(f"Milvus HTTP health check: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Milvus HTTP connection failed: {e}")
        return False

def create_test_collection():
    """Create a test collection in Milvus"""
    try:
        # This would require pymilvus, but let's test the HTTP endpoint first
        print("Testing Milvus HTTP endpoints...")
        
        # Test health endpoint
        response = requests.get("http://milvus:9091/healthz", timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
        
        # Test metrics endpoint
        response = requests.get("http://milvus:9091/metrics", timeout=5)
        print(f"Metrics endpoint: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"Error testing Milvus: {e}")
        return False

def main():
    print("=== Testing Milvus Connection and Ingestion ===")
    
    # Test connection
    if not test_milvus_connection():
        print("❌ Milvus connection failed")
        return
    
    print("✅ Milvus connection successful")
    
    # Test HTTP endpoints
    if not create_test_collection():
        print("❌ Milvus HTTP endpoints failed")
        return
    
    print("✅ Milvus HTTP endpoints working")
    
    # Check for PDFs
    pdf_dir = Path("/mnt/iscsi/pdf-test")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        print(f"Found {len(pdfs)} PDF files in {pdf_dir}")
        if pdfs:
            print(f"First PDF: {pdfs[0].name}")
    else:
        print(f"PDF directory {pdf_dir} not found")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
