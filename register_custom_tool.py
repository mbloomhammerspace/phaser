#!/usr/bin/env python3
"""
Register the custom RAG tool with NAT
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/app')

# Import and register the custom tool
try:
    from custom_rag_tool import custom_rag_tool, CustomRAGToolConfig
    print("✅ Custom RAG tool imported successfully")
    print("✅ Tool registered with NAT")
except Exception as e:
    print(f"❌ Error importing custom tool: {e}")
    sys.exit(1)




