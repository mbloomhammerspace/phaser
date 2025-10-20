#!/usr/bin/env python3
"""
Ingest PDFs from /mnt/pdf-test into a new Milvus collection
"""
import os
import sys
import hashlib
from datetime import datetime
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import PyPDF2

# Configuration
COLLECTION_NAME = 'pdf_test_docs'
PDF_DIR = '/mnt/pdf-test'
DIMENSION = 384  # Dimension for embeddings

def connect_to_milvus():
    """Connect to Milvus"""
    try:
        connections.connect(
            alias="default",
            host='milvus-external-etcd-clean',
            port='19530'
        )
        print("✅ Connected to Milvus")
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        sys.exit(1)

def create_collection():
    """Create a new collection with deduplication support"""
    # Check if collection exists
    if utility.has_collection(COLLECTION_NAME):
        print(f"⚠️  Collection '{COLLECTION_NAME}' already exists. Dropping it...")
        utility.drop_collection(COLLECTION_NAME)
    
    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4000),
        FieldSchema(name="file_hash", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="ingested_at", dtype=DataType.VARCHAR, max_length=100)
    ]
    
    schema = CollectionSchema(fields, description="PDF test documents collection")
    collection = Collection(COLLECTION_NAME, schema)
    
    # Create index
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    
    print(f"✅ Created collection: {COLLECTION_NAME}")
    return collection

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"  ⚠️  Error extracting text: {e}")
        return None

def generate_simple_embedding(text):
    """Generate a simple embedding (word count based)"""
    import hashlib
    # Create a deterministic embedding based on text
    text_hash = hashlib.md5(text.encode()).hexdigest()
    # Convert hash to numbers and normalize
    embedding = []
    for i in range(0, len(text_hash), 2):
        val = int(text_hash[i:i+2], 16) / 255.0
        embedding.append(val)
    
    # Pad or truncate to DIMENSION
    while len(embedding) < DIMENSION:
        embedding.extend(embedding[:DIMENSION - len(embedding)])
    embedding = embedding[:DIMENSION]
    
    return embedding

def ingest_pdfs(collection):
    """Ingest all PDFs from directory"""
    if not os.path.exists(PDF_DIR):
        print(f"❌ Directory not found: {PDF_DIR}")
        return
    
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    
    print(f"\n📂 Found {total_files} PDF files in {PDF_DIR}")
    print("=" * 60)
    
    ingested_count = 0
    skipped_count = 0
    error_count = 0
    seen_hashes = set()
    
    for idx, filename in enumerate(pdf_files, 1):
        filepath = os.path.join(PDF_DIR, filename)
        print(f"\n[{idx}/{total_files}] Processing: {filename}")
        
        try:
            # Calculate file hash for deduplication
            file_hash = calculate_file_hash(filepath)
            
            if file_hash in seen_hashes:
                print(f"  ⏭️  DUPLICATE - Skipping")
                skipped_count += 1
                continue
            
            seen_hashes.add(file_hash)
            
            # Extract text
            text = extract_text_from_pdf(filepath)
            if not text:
                print(f"  ⚠️  No text extracted - Skipping")
                skipped_count += 1
                continue
            
            # Truncate text to fit VARCHAR limit
            if len(text) > 3500:
                text = text[:3500]
                print(f"  ✂️  Text truncated to 3500 chars")
            
            # Generate embedding
            embedding = generate_simple_embedding(text)
            
            # Prepare data
            data = [
                [embedding],
                [filename],
                [text],
                [file_hash],
                [datetime.now().isoformat()]
            ]
            
            # Insert into Milvus
            collection.insert(data)
            ingested_count += 1
            print(f"  ✅ Ingested ({len(text)} chars)")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            error_count += 1
    
    # Flush to persist data
    collection.flush()
    print("\n" + "=" * 60)
    print(f"📊 Ingestion Summary:")
    print(f"   ✅ Successfully ingested: {ingested_count}")
    print(f"   ⏭️  Skipped (duplicates/no text): {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📦 Total in collection: {collection.num_entities}")

def main():
    print("🚀 Starting PDF ingestion from /mnt/pdf-test")
    print(f"Target collection: {COLLECTION_NAME}\n")
    
    connect_to_milvus()
    collection = create_collection()
    ingest_pdfs(collection)
    
    print("\n✅ Ingestion complete!")

if __name__ == "__main__":
    main()

