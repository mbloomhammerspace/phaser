#!/usr/bin/env python3
import requests
import json
import os

def test_ingestion():
    print("=== TESTING PDF INGESTION ===")
    
    # Test ingestor-server API
    try:
        response = requests.get('http://ingestor-server:8082/health', timeout=10)
        print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test collections
    try:
        response = requests.get('http://ingestor-server:8082/collections', timeout=10)
        print(f"Collections: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Collections check failed: {e}")
    
    # Find test PDFs
    pdf_dir = '/pdfs/pdfs'
    if os.path.exists(pdf_dir):
        test_pdfs = [f for f in os.listdir(pdf_dir) if 'test' in f.lower() and f.endswith('.pdf')]
        print(f"Found {len(test_pdfs)} test PDFs")
        
        if test_pdfs:
            test_pdf = os.path.join(pdf_dir, test_pdfs[0])
            print(f"Testing with: {test_pdfs[0]}")
            
            # Create collection first
            try:
                response = requests.post(
                    'http://ingestor-server:8082/collection',
                    json={'collection_name': 'test_collection'},
                    timeout=30
                )
                print(f"Collection creation: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Collection creation failed: {e}")
            
            # Ingest PDF
            try:
                with open(test_pdf, 'rb') as f:
                    files = {'documents': (test_pdfs[0], f, 'application/pdf')}
                    data = {'data': json.dumps({'collection_name': 'test_collection'})}
                    
                    response = requests.post(
                        'http://ingestor-server:8082/documents',
                        files=files,
                        data=data,
                        timeout=120
                    )
                    print(f"Ingestion: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Ingestion failed: {e}")
    else:
        print("PDF directory not found")

if __name__ == "__main__":
    test_ingestion()
