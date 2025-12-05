#!/usr/bin/env python3
"""
Modified NVIDIA RAG Tool for NAT v1.2.1
This replaces the existing nvidia_rag.py to use our RAG server
"""

import json
import logging
from typing import Dict, Any

from pydantic import Field

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class NVIDIARAGToolConfig(FunctionBaseConfig, name="nvidia_rag"):
    """
    Tool used to search our RAG server using the /generate endpoint
    """
    base_url: str = Field(default="http://10.0.0.25:30081", description="The base URL to the RAG service.")
    timeout: int = Field(default=60, description="The timeout configuration to use when sending requests.")
    collection_name: str = Field(default="case_1000230", description="The collection name to search.")
    max_tokens: int = Field(default=2000, description="Maximum tokens for the response.")
    temperature: float = Field(default=0.1, description="Temperature for the response.")


@register_function(config_type=NVIDIARAGToolConfig)
async def nvidia_rag_tool(config: NVIDIARAGToolConfig, builder: Builder):
    """
    Modified nvidia_rag_tool that uses our RAG server /generate endpoint
    """
    import httpx
    
    async with httpx.AsyncClient(
        headers={
            "accept": "application/json", 
            "Content-Type": "application/json"
        },
        timeout=config.timeout
    ) as client:

        async def runnable(query: str) -> str:
            try:
                url = f"{config.base_url}/generate"
                
                # Use the exact same payload format as our working curl script
                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "use_knowledge_base": True,
                    "collection_names": [config.collection_name],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "stream": False
                }
                
                logger.debug("Sending request to RAG endpoint %s", url)
                response = await client.post(url, content=json.dumps(payload))
                
                response.raise_for_status()
                
                # Handle streaming response
                response_text = response.text
                
                if response_text.startswith('data:'):
                    # Process streaming response
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
                    
                    full_content = ''.join(content_parts)
                    
                    # Format response with citations
                    result = f"**RAG Search Results:**\n\n{full_content}\n\n"
                    
                    if citations:
                        result += f"**Citations ({len(citations)} documents):**\n"
                        for i, citation in enumerate(citations[:5], 1):
                            doc_name = citation.get('document_name', 'Unknown')
                            result += f"{i}. {doc_name}\n"
                    
                    return result
                else:
                    # Handle regular JSON response
                    try:
                        data = response.json()
                        content = data['choices'][0]['message']['content']
                        citations = data.get('citations', {}).get('results', [])
                        
                        result = f"**RAG Search Results:**\n\n{content}\n\n"
                        
                        if citations:
                            result += f"**Citations ({len(citations)} documents):**\n"
                            for i, citation in enumerate(citations[:5], 1):
                                doc_name = citation.get('document_name', 'Unknown')
                                result += f"{i}. {doc_name}\n"
                        
                        return result
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error("JSON parsing error: %s", e)
                        return f"Error parsing response: {e}"
                        
            except Exception as e:
                logger.exception("Error while running the RAG tool", exc_info=True)
                return f"Error while running the RAG tool: {e}"

        yield FunctionInfo.from_fn(
            runnable,
            description="Search documents using the RAG pipeline with the /generate endpoint"
        )







