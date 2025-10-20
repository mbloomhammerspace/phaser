#!/usr/bin/env python3
import requests
import json
import os
import time

def test_ingestion_pipeline():
    print("=== TESTING INGESTION PIPELINE ===")
    
    # Find a test PDF
    pdf_dir = "/pdfs/pdfs"
    test_pdfs = [f for f in os.listdir(pdf_dir) if 'test' in f.lower() and f.endswith('.pdf')]
    
    if not test_pdfs:
        print("❌ No test PDFs found")
        return
    
    test_pdf = os.path.join(pdf_dir, test_pdfs[0])
    print(f"📄 Testing with: {test_pdfs[0]}")
    
    # Test 1: Check if we can read the file
    try:
        with open(test_pdf, 'rb') as f:
            file_size = len(f.read())
        print(f"✅ File readable, size: {file_size} bytes")
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
        return
    
    # Test 2: Try Ingestor Server API
    print("\n🔧 Testing Ingestor Server API...")
    try:
        with open(test_pdf, 'rb') as f:
            files = {'files': (test_pdfs[0], f, 'application/pdf')}
            data = {'collection_name': 'test_collection'}
            
            response = requests.post(
                'http://ingestor-server:8082/documents',
                files=files,
                data=data,
                timeout=120
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ Ingestor Server API: SUCCESS")
            else:
                print("❌ Ingestor Server API: FAILED")
                
    except Exception as e:
        print(f"❌ Ingestor Server API Error: {e}")
    
    # Test 3: Check collections
    print("\n📊 Checking collections...")
    try:
        response = requests.get('http://ingestor-server:8082/collections', timeout=30)
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Collections: {collections}")
        else:
            print(f"❌ Collections check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Collections check error: {e}")

if __name__ == "__main__":
    test_ingestion_pipeline()
