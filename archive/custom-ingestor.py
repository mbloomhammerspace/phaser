#!/usr/bin/env python3
"""
Custom ingestor server that mimics NVIDIA Blueprint ingestor
Uses pymilvus, PyPDF2, and embedding service
"""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import PyPDF2
import requests
import hashlib
import io
import json
from typing import List
import uuid

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
MILVUS_HOST = "milvus"
MILVUS_PORT = 19530
EMBEDDING_URL = "http://embedding-service:8000/v1/embeddings"

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

@app.get("/v1/health")
async def health():
    return {"message": "Ingestion Service is up."}

@app.get("/v1/collections")
async def list_collections():
    collections = utility.list_collections()
    result = []
    for coll_name in collections:
        coll = Collection(coll_name)
        coll.load()
        result.append({
            "collection_name": coll_name,
            "num_entities": coll.num_entities,
            "metadata_schema": []
        })
    return {
        "message": "Collections listed successfully.",
        "total_collections": len(result),
        "collections": result
    }

@app.post("/v1/collections")
async def create_collections(collection_names: List[str]):
    successful = []
    failed = []
    
    for name in collection_names:
        try:
            if utility.has_collection(name):
                successful.append(name)
                continue
            
            fields = [
                FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4000),
                FieldSchema(name="content_metadata", dtype=DataType.JSON)
            ]
            
            schema = CollectionSchema(fields, description=f"Collection {name}")
            collection = Collection(name, schema)
            
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="vector", index_params=index_params)
            successful.append(name)
        except Exception as e:
            failed.append({"collection_name": name, "error_message": str(e)})
    
    return {
        "message": "Collection creation process completed.",
        "successful": successful,
        "failed": failed,
        "total_success": len(successful),
        "total_failed": len(failed)
    }

@app.post("/v1/documents")
async def ingest_documents(
    documents: List[UploadFile] = File(...),
    data: str = Form(...)
):
    try:
        metadata = json.loads(data) if isinstance(data, str) else data
        collection_name = metadata.get("collection_name", "default")
        
        # Create collection if doesn't exist
        if not utility.has_collection(collection_name):
            await create_collections([collection_name])
        
        collection = Collection(collection_name)
        collection.load()
        
        task_id = str(uuid.uuid4())
        
        for doc in documents:
            # Extract text
            content = await doc.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if len(text) > 3500:
                text = text[:3500]
            
            # Get embedding
            emb_response = requests.post(
                EMBEDDING_URL,
                json={"input": [text]},
                timeout=60
            )
            embedding = emb_response.json()["data"][0]["embedding"]
            
            # Insert
            data_to_insert = [
                [embedding],
                [doc.filename],
                [text],
                [{}]
            ]
            collection.insert(data_to_insert)
        
        collection.flush()
        
        return {
            "message": "Ingestion started in background",
            "task_id": task_id
        }
    
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)

