#!/usr/bin/env python3
import os
import requests
import time
from pathlib import Path

INGESTOR_URL = "http://ingestor-server:8082/v1"
PDF_DIR = "/mnt/pdf-test"
COLLECTION = "pdf_test_docs"

pdfs = sorted([f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')])
total = len(pdfs)

print(f"🚀 Ingesting {total} PDFs into {COLLECTION}")
print("="*70)

success = 0
failed = 0

for idx, filename in enumerate(pdfs, 1):
    filepath = os.path.join(PDF_DIR, filename)
    print(f"\n[{idx}/{total}] {filename}")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'documents': (filename, f, 'application/pdf')}
            import json
            data = {'data': json.dumps({'collection_name': COLLECTION})}
            
            r = requests.post(
                f"{INGESTOR_URL}/documents",
                files=files,
                data=data,
                timeout=120
            )
            
            if r.status_code in [200, 201, 202]:
                print(f"  ✅ Uploaded")
                success += 1
            else:
                print(f"  ❌ Failed: {r.status_code}")
                failed += 1
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        failed += 1
    
    time.sleep(0.5)

print(f"\n{'='*70}")
print(f"📊 Results: ✅ {success} | ❌ {failed}")
