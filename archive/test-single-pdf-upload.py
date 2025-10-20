#!/usr/bin/env python3
import requests
import time

INGESTOR_URL = "http://localhost:8082/v1"
PDF_PATH = "/mnt/pdf-test/DEV-NFS-140725-1219-1825.pdf"
COLLECTION = "pdf_test_docs"

print("Testing single PDF upload to verify pipeline...")
print(f"File: DEV-NFS-140725-1219-1825.pdf")
print(f"Collection: {COLLECTION}\n")

# This would be run from your Mac with port-forward active
print("Note: Run this after setting up port-forward:")
print("  kubectl port-forward svc/ingestor-server 8082:8082")
print("\nSkipping actual upload - use playground UI or run ingestion job in cluster")

