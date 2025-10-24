# NAT RAG Integration Guide

## Overview
This guide explains how to update the NeMo Agent Toolkit (NAT) container to use the working RAG server endpoint.

## Current Status
- ✅ RAG server working at: `http://10.0.0.25:30081`
- ✅ Collection `case_1000230` accessible
- ✅ API parameters confirmed: `use_knowledge_base: true`, `collection_names: ["case_1000230"]`

## Files Created
1. `nat-rag-workflow.yml` - Updated workflow configuration
2. `nat-rag-test.py` - Python test script for the container
3. `test-rag-api.sh` - Bash test script (already working)

## Steps to Update NAT Container

### 1. Copy Files to Jumphost
```bash
# Copy the files to the jumphost (10.0.0.236)
scp nat-rag-workflow.yml ubuntu@10.0.0.236:~/
scp nat-rag-test.py ubuntu@10.0.0.236:~/
scp test-rag-api.sh ubuntu@10.0.0.236:~/
```

### 2. Access the NAT Container
```bash
# SSH to jumphost
ssh ubuntu@10.0.0.236

# Access the NAT container
docker exec -it nemo-agent-toolkit-host bash
```

### 3. Copy Files into Container
```bash
# From inside the container, copy files from host
docker cp nat-rag-workflow.yml nemo-agent-toolkit-host:/app/workflows/
docker cp nat-rag-test.py nemo-agent-toolkit-host:/app/
docker cp test-rag-api.sh nemo-agent-toolkit-host:/app/
```

### 4. Install Python Dependencies (if needed)
```bash
# Inside the container
pip install requests
```

### 5. Test the RAG Endpoint
```bash
# Test with Python script
python3 /app/nat-rag-test.py

# Test with bash script
bash /app/test-rag-api.sh

# Test with NAT workflow
nat run /app/workflows/nat-rag-workflow.yml
```

## Updated Workflow Configuration

The `nat-rag-workflow.yml` includes:
- **RAG search function**: Uses the working endpoint `http://10.0.0.25:30081`
- **Milvus backup**: Direct Milvus access as fallback
- **Proper parameters**: `use_knowledge_base: true`, `collection_names: ["case_1000230"]`

## Key Changes Made
1. **Correct endpoint**: `http://10.0.0.25:30081/generate`
2. **Proper API format**: OpenAI chat completion format with `messages`
3. **Collection specification**: `collection_names: ["case_1000230"]`
4. **Knowledge base enabled**: `use_knowledge_base: true`

## Testing
Run the test scripts to verify:
- Network connectivity to RAG server
- API parameter format
- Response parsing
- Workflow execution

## Troubleshooting
- If connection fails: Check network routing from jumphost to 10.0.0.25
- If API fails: Verify the exact parameters used in the working curl test
- If workflow fails: Check NAT dependency issues (langchain/langgraph)
