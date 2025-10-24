# NAT-RAG Integration Guide

This guide shows how to integrate the NVIDIA Agent Toolkit (NAT) with our RAG pipeline using custom wrapper functions.

## Overview

The integration consists of:
1. **`nat-rag-wrapper.py`** - Custom Python wrapper that provides NAT-compatible functions
2. **`nat-rag-workflow.yml`** - NAT workflow configuration that uses our RAG functions
3. **Direct RAG server integration** - Bypasses NAT dependency issues

## Files Created

### 1. `nat-rag-wrapper.py`
- **`RAGPipelineWrapper`** class for direct RAG server communication
- **`rag_search_function()`** - NAT-compatible single collection search
- **`rag_multi_search_function()`** - NAT-compatible multi-collection search
- Handles streaming responses from RAG server
- Provides error handling and health checks

### 2. `nat-rag-workflow.yml`
- NAT workflow configuration
- Defines custom functions that wrap our RAG pipeline
- Multi-step workflow: initial search → multi-collection search → LLM synthesis
- Uses existing `nim-llm` for analysis

## Setup Instructions

### 1. Copy Files to NAT Container
```bash
# Copy the wrapper and workflow files
docker cp nat-rag-wrapper.py nemo-agent-toolkit-host:/app/
docker cp nat-rag-workflow.yml nemo-agent-toolkit-host:/app/
```

### 2. Install Dependencies in Container
```bash
# Access the container
docker exec -it nemo-agent-toolkit-host bash
cd /app

# Install required packages
pip install requests
```

### 3. Test the Wrapper Functions
```bash
# Test single collection search
python3 nat-rag-wrapper.py "Do a deep analysis of travel expenses and anomalies"

# Test multi-collection search
python3 nat-rag-wrapper.py "Find unusual spending patterns" --multi case_1000230,case_1000231,case_1000232
```

### 4. Run NAT Workflow
```bash
# Run the integrated workflow
nat run workflow.yml --input "Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures"
```

## How It Works

### RAG Pipeline Integration
1. **Direct API Calls**: Wrapper functions make direct HTTP calls to RAG server (`http://10.0.0.25:30081`)
2. **Streaming Support**: Handles both streaming and regular JSON responses
3. **Error Handling**: Comprehensive error handling for network issues, timeouts, and parsing errors
4. **Collection Support**: Works with all available case collections

### NAT Workflow Process
1. **Initial Search**: Searches primary collection (`case_1000230`)
2. **Multi-Collection Search**: Searches across 5 collections for broader coverage
3. **LLM Synthesis**: Uses `nim-llm` to analyze and synthesize results
4. **Comprehensive Output**: Provides detailed analysis with citations

### Key Features
- **Bypasses NAT Dependencies**: No reliance on problematic `langchain`/`langgraph` versions
- **Direct RAG Integration**: Uses our working RAG server API
- **Multi-Collection Support**: Searches across multiple case collections
- **LLM Analysis**: Leverages existing NIM for intelligent synthesis
- **Error Resilient**: Handles network issues and API errors gracefully

## Usage Examples

### Simple Search
```bash
python3 nat-rag-wrapper.py "Find travel expenses over $1000"
```

### Multi-Collection Analysis
```bash
python3 nat-rag-wrapper.py "Analyze spending patterns" --multi case_1000230,case_1000231,case_1000232
```

### NAT Workflow Execution
```bash
nat run workflow.yml --input "Do a deep analysis of the files in this collection for inconsistencies or anomalies in travel and expenses, project any planned travel or large cash expenditures"
```

## Troubleshooting

### Common Issues
1. **Connection Refused**: Ensure RAG server port-forward is active
2. **Import Errors**: Make sure `requests` is installed in container
3. **Workflow Errors**: Check that `nim-llm` is running and accessible

### Health Checks
```bash
# Test RAG server connectivity
python3 -c "from nat_rag_wrapper import RAGPipelineWrapper; print(RAGPipelineWrapper().health_check())"

# Test NAT workflow
nat run workflow.yml --input "test query"
```

## Benefits

✅ **No Dependency Issues**: Bypasses all `langchain`/`langgraph` problems  
✅ **Direct RAG Access**: Uses our working RAG server API  
✅ **Multi-Collection Support**: Searches across multiple case collections  
✅ **LLM Integration**: Leverages existing NIM for analysis  
✅ **Error Resilient**: Comprehensive error handling  
✅ **NAT Compatible**: Works with NAT workflow system  

This approach gives you the best of both worlds: NAT's workflow capabilities with our working RAG pipeline, without the dependency headaches.
