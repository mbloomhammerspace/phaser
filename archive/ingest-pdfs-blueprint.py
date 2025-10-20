#!/usr/bin/env python3
"""
Ingest PDFs using NVIDIA Blueprint Ingestor API
This uses the full NIM pipeline for proper PDF processing
"""
import os
import sys
import time
import hashlib
import requests
from pathlib import Path

# Configuration
INGESTOR_URL = "http://ingestor-server:8082/v1"
COLLECTION_NAME = "pdf_test_docs"
PDF_DIR = "/mnt/pdf-test"

def check_ingestor_health():
    """Check if ingestor service is healthy"""
    try:
        response = requests.get(f"{INGESTOR_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Ingestor service is healthy")
            return True
        else:
            print(f"⚠️  Ingestor returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach ingestor: {e}")
        return False

def create_collection():
    """Create a new collection via API"""
    try:
        # Check if collection exists
        response = requests.get(f"{INGESTOR_URL}/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json()
            if COLLECTION_NAME in [c.get('name') for c in collections]:
                print(f"⚠️  Collection '{COLLECTION_NAME}' already exists")
                choice = input("Delete and recreate? (y/n): ")
                if choice.lower() == 'y':
                    print(f"Deleting existing collection...")
                    requests.delete(f"{INGESTOR_URL}/collections/{COLLECTION_NAME}", timeout=30)
                    time.sleep(2)
        
        # Create new collection
        print(f"Creating collection: {COLLECTION_NAME}")
        payload = {
            "collection_name": COLLECTION_NAME,
            "dimension": 1024,  # NVIDIA NIM embedding dimension
            "description": "PDF test documents processed with NVIDIA Blueprint"
        }
        response = requests.post(f"{INGESTOR_URL}/collections", json=payload, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ Collection created: {COLLECTION_NAME}")
            return True
        else:
            print(f"⚠️  Collection creation returned: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return True  # Continue anyway, might already exist
            
    except Exception as e:
        print(f"⚠️  Collection setup: {e}")
        return True  # Continue anyway

def calculate_file_hash(filepath):
    """Calculate SHA256 hash for deduplication"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def ingest_pdf(pdf_path, filename):
    """Ingest a single PDF using the Blueprint ingestor API"""
    try:
        # Prepare multipart form data
        with open(pdf_path, 'rb') as f:
            files = {
                'documents': (filename, f, 'application/pdf')
            }
            
            data = {
                'data': f'{{"collection_name": "{COLLECTION_NAME}"}}'
            }
            
            print(f"  📤 Uploading to ingestor...")
            response = requests.post(
                f"{INGESTOR_URL}/documents",
                files=files,
                data=data,
                timeout=300  # 5 minutes for large PDFs
            )
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                print(f"  ✅ Ingested successfully")
                
                # Check for task ID (async processing)
                if 'task_id' in result:
                    task_id = result['task_id']
                    print(f"  ⏳ Task ID: {task_id} (processing...)")
                    # Could poll task status here
                
                return True
            else:
                print(f"  ❌ Failed: HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
                
    except requests.exceptions.Timeout:
        print(f"  ⏱️  Timeout (file may still be processing)")
        return False
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
        return False

def ingest_all_pdfs():
    """Ingest all PDFs from directory"""
    if not os.path.exists(PDF_DIR):
        print(f"❌ Directory not found: {PDF_DIR}")
        return
    
    pdf_files = sorted([f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')])
    total_files = len(pdf_files)
    
    if total_files == 0:
        print(f"❌ No PDF files found in {PDF_DIR}")
        return
    
    print(f"\n📂 Found {total_files} PDF files in {PDF_DIR}")
    print("=" * 70)
    
    ingested_count = 0
    failed_count = 0
    seen_hashes = set()
    
    for idx, filename in enumerate(pdf_files, 1):
        filepath = os.path.join(PDF_DIR, filename)
        print(f"\n[{idx}/{total_files}] {filename}")
        
        try:
            # Check for duplicates
            file_hash = calculate_file_hash(filepath)
            
            if file_hash in seen_hashes:
                print(f"  ⏭️  DUPLICATE - Skipping")
                continue
            
            seen_hashes.add(file_hash)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            print(f"  📏 Size: {file_size / 1024:.1f} KB")
            
            # Ingest via Blueprint API
            if ingest_pdf(filepath, filename):
                ingested_count += 1
            else:
                failed_count += 1
            
            # Small delay between files
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)[:100]}")
            failed_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Ingestion Summary:")
    print(f"   ✅ Successfully ingested: {ingested_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📦 Total processed: {ingested_count + failed_count} / {total_files}")

def main():
    print("🚀 NVIDIA Blueprint PDF Ingestion")
    print(f"   Collection: {COLLECTION_NAME}")
    print(f"   Source: {PDF_DIR}")
    print(f"   Ingestor: {INGESTOR_URL}\n")
    
    if not check_ingestor_health():
        print("❌ Ingestor service not available")
        sys.exit(1)
    
    create_collection()
    ingest_all_pdfs()
    
    print("\n✅ Ingestion complete!")
    print(f"\n💡 Check results in playground at collection: {COLLECTION_NAME}")

if __name__ == "__main__":
    main()

