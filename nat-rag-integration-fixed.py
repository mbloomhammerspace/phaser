#!/usr/bin/env python3
"""
NVIDIA Agent Toolkit - RAG Pipeline Integration (Fixed for Streaming)
Handles streaming responses from RAG server
"""

import requests
import json
import sys
import re

def search_rag_pipeline(query, collection="case_1000230"):
    """Search RAG pipeline with proper streaming handling"""
    
    rag_server_url = "http://10.0.0.25:30081"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "use_knowledge_base": True,
        "collection_names": [collection],
        "max_tokens": 2000,
        "temperature": 0.1,
        "stream": False  # Try non-streaming first
    }
    
    try:
        print(f"🔍 Searching RAG pipeline...")
        print(f"Query: {query}")
        print(f"Collection: {collection}")
        print(f"Server: {rag_server_url}")
        print()
        
        response = requests.post(
            f"{rag_server_url}/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_text = response.text
            print(f"📝 Response type: {'Streaming' if response_text.startswith('data:') else 'JSON'}")
            
            if response_text.startswith('data:'):
                # Handle streaming response
                print("🔄 Processing streaming response...")
                content_parts = []
                citations = []
                
                lines = response_text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            
                            # Extract content
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'message' in choice and 'content' in choice['message']:
                                    content_parts.append(choice['message']['content'])
                                elif 'delta' in choice and 'content' in choice['delta']:
                                    content_parts.append(choice['delta']['content'])
                            
                            # Extract citations
                            if 'citations' in data and 'results' in data['citations']:
                                citations.extend(data['citations']['results'])
                                
                        except json.JSONDecodeError:
                            continue
                
                # Combine content
                full_content = ''.join(content_parts)
                
                print("✅ Search successful!")
                print()
                print("Response:")
                print("========")
                print(full_content)
                
                if citations:
                    print()
                    print(f"📚 Citations ({len(citations)} documents):")
                    for i, citation in enumerate(citations[:5], 1):
                        doc_name = citation.get('document_name', 'Unknown')
                        print(f"  {i}. {doc_name}")
                
                return full_content
            else:
                # Handle regular JSON response
                try:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    print("✅ Search successful!")
                    print()
                    print("Response:")
                    print("========")
                    print(content)
                    return content
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response: {response_text[:500]}")
                    return None
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to RAG server")
        return None
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nat-rag-integration-fixed.py '<query>' [collection]")
        sys.exit(1)
    
    query = sys.argv[1]
    collection = sys.argv[2] if len(sys.argv) > 2 else "case_1000230"
    
    result = search_rag_pipeline(query, collection)
    
    if result:
        print()
        print("✅ Search completed successfully!")
    else:
        print()
        print("❌ Search failed!")

if __name__ == "__main__":
    main()
