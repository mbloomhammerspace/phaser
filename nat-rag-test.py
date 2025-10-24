#!/usr/bin/env python3
"""
NAT RAG Integration Test Script
Tests the RAG server endpoint from within the NAT container
"""

import requests
import json
import sys

# RAG Server Configuration
RAG_SERVER_URL = "http://10.0.0.25:30081"
COLLECTION_NAME = "case_1000230"

def test_rag_endpoint():
    """Test the RAG server endpoint with a travel analysis query"""
    
    print("🧪 Testing RAG Server from NAT Container")
    print("=======================================")
    print(f"Server: {RAG_SERVER_URL}")
    print(f"Collection: {COLLECTION_NAME}")
    print()
    
    # Test query
    query = "Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "use_knowledge_base": True,
        "collection_names": [COLLECTION_NAME],
        "max_tokens": 2000,
        "temperature": 0.1,
        "stream": False  # Get complete response
    }
    
    try:
        print("📝 Sending query to RAG server...")
        response = requests.post(
            f"{RAG_SERVER_URL}/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ RAG server responded successfully!")
            print()
            print("Response:")
            print("=========")
            
            # Parse the response
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(content)
                
                # Show citations if available
                if 'citations' in data:
                    citations = data['citations']
                    print(f"\n📚 Citations: {citations.get('total_results', 0)} documents found")
                    for i, result in enumerate(citations.get('results', [])[:3], 1):
                        print(f"  {i}. {result.get('document_name', 'Unknown')}")
            else:
                print("No content in response")
                print(json.dumps(data, indent=2))
        else:
            print(f"❌ RAG server error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - cannot reach RAG server")
        print("Check network connectivity to 10.0.0.25:30081")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test RAG server health endpoint"""
    try:
        response = requests.get(f"{RAG_SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ RAG server health check passed")
            health_data = response.json()
            print(f"Databases: {health_data.get('databases', [])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("Testing RAG server connectivity from NAT container...")
    print()
    
    # Test health first
    test_health()
    print()
    
    # Test main endpoint
    test_rag_endpoint()
    
    print()
    print("✅ Test completed!")
