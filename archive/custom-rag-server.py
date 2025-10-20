#!/usr/bin/env python3
"""Custom RAG server"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import requests
from pymilvus import connections, Collection
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LLM_URL = "http://nim-llm:8000/v1/chat/completions"
EMBEDDING_URL = "http://embedding-service:8000/v1/embeddings"
MILVUS_HOST = "milvus"
MILVUS_PORT = 19530

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

@app.post("/v1/generate")
async def generate(request: dict):
    messages = request.get("messages", [])
    use_kb = request.get("use_knowledge_base", False)
    collection_names = request.get("collection_names", [])
    
    context = ""
    if use_kb and collection_names:
        # Get context from Milvus
        query = messages[-1]["content"]
        emb_response = requests.post(EMBEDDING_URL, json={"input": [query]}, timeout=30)
        query_embedding = emb_response.json()["data"][0]["embedding"]
        
        for coll_name in collection_names:
            try:
                collection = Collection(coll_name)
                collection.load()
                results = collection.search(
                    data=[query_embedding],
                    anns_field="vector",
                    param={"metric_type": "L2", "params": {"nprobe": 10}},
                    limit=5,
                    output_fields=["text", "source"]
                )
                
                for hits in results:
                    for hit in hits:
                        context += f"\n{hit.entity.get('text')}\n"
            except:
                pass
    
    # Build prompt
    if context:
        system_msg = f"Use the following context to answer the question:\n{context}"
        messages = [{"role": "system", "content": system_msg}] + messages
    
    # Call LLM
    llm_payload = {
        "model": "meta/llama3-8b-instruct",
        "messages": messages,
        "max_tokens": request.get("max_tokens", 512),
        "temperature": request.get("temperature", 0.7),
        "stream": True
    }
    
    def generate_stream():
        try:
            resp = requests.post(LLM_URL, json=llm_payload, stream=True, timeout=120)
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            continue
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and data['choices']:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    yield f"data: {{\"id\":\"{uuid.uuid4()}\",\"choices\":[{{\"index\":0,\"message\":{{\"role\":\"assistant\",\"content\":\"{content}\"}},\"delta\":{{\"role\":null,\"content\":\"{content}\"}},\"finish_reason\":null}}],\"model\":\"meta/llama3-8b-instruct\",\"object\":\"chat.completion.chunk\",\"created\":0,\"usage\":{{\"total_tokens\":0,\"prompt_tokens\":0,\"completion_tokens\":0}},\"citations\":{{\"total_results\":0,\"results\":[]}}}}\n\n"
                        except:
                            pass
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.get("/v1/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)

