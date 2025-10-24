#!/usr/bin/env python3
"""
Purge Case Collections from Milvus

This script connects to Milvus and drops all collections that start with "case_".
"""

import os
import sys
from pymilvus import connections, utility

def main():
    print("🗑️  Purging case collections from Milvus...")
    
    # Try different connection methods
    connection_methods = [
        # Method 1: Direct connection to Milvus service
        {"host": "milvus-standalone", "port": "19530"},
        {"host": "10.233.53.224", "port": "19530"},
        {"host": "localhost", "port": "19530"},
    ]
    
    connected = False
    for method in connection_methods:
        try:
            print(f"Trying to connect to {method['host']}:{method['port']}...")
            connections.connect("default", host=method["host"], port=method["port"])
            print(f"✅ Connected to Milvus at {method['host']}:{method['port']}")
            connected = True
            break
        except Exception as e:
            print(f"❌ Failed to connect to {method['host']}:{method['port']} - {e}")
            continue
    
    if not connected:
        print("❌ Could not connect to Milvus. Please check if Milvus is running.")
        return 1
    
    try:
        # List all collections
        collections = utility.list_collections()
        print(f"\n📋 Found {len(collections)} collections:")
        for col in collections:
            print(f"  - {col}")
        
        # Find case collections
        case_collections = [col for col in collections if col.startswith("case_")]
        
        if not case_collections:
            print("\n✅ No case collections found to purge.")
            return 0
        
        print(f"\n🗑️  Dropping {len(case_collections)} case collections:")
        dropped_count = 0
        
        for col in case_collections:
            try:
                utility.drop_collection(col)
                print(f"  ✅ Dropped: {col}")
                dropped_count += 1
            except Exception as e:
                print(f"  ❌ Failed to drop {col}: {e}")
        
        # List remaining collections
        remaining = utility.list_collections()
        print(f"\n📋 Remaining collections ({len(remaining)}):")
        for col in remaining:
            print(f"  - {col}")
        
        print(f"\n✅ Successfully dropped {dropped_count} case collections.")
        return 0
        
    except Exception as e:
        print(f"❌ Error managing collections: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())



