#!/usr/bin/env python3
"""
NVIDIA Agent Toolkit - RAG Pipeline Wrapper
Custom NAT function that integrates with our working RAG server
"""

import requests
import json
import re
from typing import Dict, List, Any, Optional

class RAGPipelineWrapper:
    """Wrapper class to integrate RAG pipeline with NAT toolkit"""
    
    def __init__(self, rag_server_url: str = "http://10.0.0.25:30081"):
        self.rag_server_url = rag_server_url
        self.available_collections = [
            "case_1000230", "case_1000231", "case_1000232", "case_1000233", 
            "case_1000234", "case_1000235", "case_1000236", "case_1000237",
            "case_1000238", "case_1000239", "case_1000240", "case_1000241",
            "case_1000242", "case_1000243", "case_1000244", "case_1000245",
            "case_1000246", "case_1000247", "case_1000248", "case_1000249",
            "case_1000250", "case_1000251", "case_1000252", "case_1000253",
            "case_1000254", "case_1000255", "case_1000256", "case_1000257"
        ]
    
    def search_documents(self, query: str, collection: str = "case_1000230", max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Search documents using RAG pipeline - NAT compatible function
        
        Args:
            query: Search query
            collection: Collection name to search
            max_tokens: Maximum tokens for response
            
        Returns:
            Dict with search results, content, and citations
        """
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "use_knowledge_base": True,
            "collection_names": [collection],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.rag_server_url}/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                response_text = response.text
                
                if response_text.startswith('data:'):
                    # Handle streaming response
                    content_parts = []
                    citations = []
                    
                    lines = response_text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                
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
                    
                    full_content = ''.join(content_parts)
                    
                    return {
                        "success": True,
                        "content": full_content,
                        "citations": citations,
                        "collection": collection,
                        "query": query
                    }
                else:
                    # Handle regular JSON response
                    try:
                        data = response.json()
                        content = data['choices'][0]['message']['content']
                        citations = data.get('citations', {}).get('results', [])
                        
                        return {
                            "success": True,
                            "content": content,
                            "citations": citations,
                            "collection": collection,
                            "query": query
                        }
                    except (json.JSONDecodeError, KeyError):
                        return {
                            "success": False,
                            "error": "JSON parsing error",
                            "raw_response": response_text[:500]
                        }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to RAG server"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_multiple_collections(self, query: str, collections: List[str] = None) -> Dict[str, Any]:
        """
        Search across multiple collections
        
        Args:
            query: Search query
            collections: List of collection names (defaults to all case collections)
            
        Returns:
            Dict with combined results from all collections
        """
        if collections is None:
            collections = self.available_collections[:5]  # Limit to first 5 for performance
        
        all_results = []
        successful_searches = 0
        
        for collection in collections:
            result = self.search_documents(query, collection)
            if result["success"]:
                all_results.append({
                    "collection": collection,
                    "content": result["content"],
                    "citations": result["citations"]
                })
                successful_searches += 1
        
        return {
            "success": successful_searches > 0,
            "total_collections": len(collections),
            "successful_searches": successful_searches,
            "results": all_results,
            "query": query
        }
    
    def get_available_collections(self) -> List[str]:
        """Get list of available collections"""
        return self.available_collections
    
    def health_check(self) -> Dict[str, Any]:
        """Check RAG server health"""
        try:
            response = requests.get(f"{self.rag_server_url}/health", timeout=10)
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# NAT-compatible function wrapper
def rag_search_function(query: str, collection: str = "case_1000230") -> str:
    """
    NAT-compatible function for RAG search
    This function can be called from NAT workflows
    """
    wrapper = RAGPipelineWrapper()
    result = wrapper.search_documents(query, collection)
    
    if result["success"]:
        response = f"Search Results for '{query}' in collection '{collection}':\n\n"
        response += f"Content: {result['content']}\n\n"
        
        if result["citations"]:
            response += f"Citations ({len(result['citations'])} documents):\n"
            for i, citation in enumerate(result["citations"][:5], 1):
                doc_name = citation.get('document_name', 'Unknown')
                response += f"  {i}. {doc_name}\n"
        
        return response
    else:
        return f"Search failed: {result['error']}"

def rag_multi_search_function(query: str, collections: List[str] = None) -> str:
    """
    NAT-compatible function for multi-collection search
    """
    wrapper = RAGPipelineWrapper()
    result = wrapper.search_multiple_collections(query, collections)
    
    if result["success"]:
        response = f"Multi-Collection Search Results for '{query}':\n\n"
        response += f"Searched {result['total_collections']} collections, {result['successful_searches']} successful\n\n"
        
        for i, search_result in enumerate(result["results"], 1):
            response += f"Collection {i}: {search_result['collection']}\n"
            response += f"Content: {search_result['content'][:200]}...\n\n"
        
        return response
    else:
        return f"Multi-search failed: No successful searches"

# Example usage for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 nat-rag-wrapper.py '<query>' [collection]")
        print("       python3 nat-rag-wrapper.py '<query>' --multi [collection1,collection2,...]")
        sys.exit(1)
    
    query = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--multi":
        # Multi-collection search
        collections = sys.argv[3].split(',') if len(sys.argv) > 3 else None
        result = rag_multi_search_function(query, collections)
        print(result)
    else:
        # Single collection search
        collection = sys.argv[2] if len(sys.argv) > 2 else "case_1000230"
        result = rag_search_function(query, collection)
        print(result)
