#!/usr/bin/env python3
"""
NVIDIA Agent Toolkit - RAG Pipeline Integration
Allows NAT to search collections through the RAG server
"""

import requests
import json
import sys
import os
from typing import Dict, List, Optional

class RAGPipelineConnector:
    """Connector class for NAT to interact with RAG pipeline"""
    
    def __init__(self, rag_server_url: str = "http://10.0.0.25:30081"):
        self.rag_server_url = rag_server_url
        self.default_collection = "case_1000230"
    
    def search_collection(self, query: str, collection_name: str = None, 
                         max_tokens: int = 2000, temperature: float = 0.1) -> Dict:
        """
        Search a collection through the RAG pipeline
        
        Args:
            query: Search query
            collection_name: Collection to search (defaults to case_1000230)
            max_tokens: Maximum tokens in response
            temperature: Response temperature
            
        Returns:
            Dictionary with search results
        """
        if collection_name is None:
            collection_name = self.default_collection
            
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "use_knowledge_base": True,
            "collection_names": [collection_name],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False  # Get complete response
        }
        
        try:
            response = requests.post(
                f"{self.rag_server_url}/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "query": query,
                    "collection": collection_name
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query": query,
                    "collection": collection_name
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to RAG server",
                "query": query,
                "collection": collection_name
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out",
                "query": query,
                "collection": collection_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "collection": collection_name
            }
    
    def extract_content(self, result: Dict) -> str:
        """Extract content from RAG response"""
        if not result["success"]:
            return f"Error: {result['error']}"
        
        data = result["data"]
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            return "No content found in response"
    
    def extract_citations(self, result: Dict) -> List[Dict]:
        """Extract citations from RAG response"""
        if not result["success"]:
            return []
        
        data = result["data"]
        if 'citations' in data:
            return data['citations'].get('results', [])
        return []
    
    def list_available_collections(self) -> List[str]:
        """List available collections (placeholder - would need Milvus connection)"""
        # This would typically connect to Milvus to list collections
        # For now, return known collections
        return ["case_1000230", "simple_test_collection"]
    
    def health_check(self) -> bool:
        """Check if RAG server is healthy"""
        try:
            response = requests.get(f"{self.rag_server_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 nat-rag-integration.py '<query>' [collection_name]")
        print("Example: python3 nat-rag-integration.py 'Find travel expenses' case_1000230")
        sys.exit(1)
    
    query = sys.argv[1]
    collection = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize connector
    connector = RAGPipelineConnector()
    
    print(f"🔍 Searching RAG pipeline...")
    print(f"Query: {query}")
    print(f"Collection: {collection or connector.default_collection}")
    print()
    
    # Perform search
    result = connector.search_collection(query, collection)
    
    if result["success"]:
        print("✅ Search successful!")
        print()
        print("Response:")
        print("========")
        content = connector.extract_content(result)
        print(content)
        
        # Show citations
        citations = connector.extract_citations(result)
        if citations:
            print()
            print(f"📚 Citations ({len(citations)} documents):")
            for i, citation in enumerate(citations[:5], 1):
                doc_name = citation.get('document_name', 'Unknown')
                print(f"  {i}. {doc_name}")
    else:
        print("❌ Search failed!")
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
