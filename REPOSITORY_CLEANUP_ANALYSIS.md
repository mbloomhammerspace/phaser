# Repository Cleanup Analysis
## File Classification and Archive Recommendations

**Generated:** October 23, 2025  
**Total Files Analyzed:** 103+ YAML/Python/Shell files

---

## 🟢 **KEEP IN ROOT - Core System Files**

### **Essential Configuration & Documentation**
- `README.md` - Main documentation
- `NVIDIA_BLUEPRINT_SOFTWARE_MANIFEST.md` - Software manifest
- `manage-port-forwards.sh` - Active port forwarding script
- `rag-blueprint-values.yaml` - Active blueprint configuration
- `rag-playground-build.tar.gz` - Frontend build artifact

### **Active NAT RAG Integration**
- `nat-rag-wrapper.py` - Core RAG wrapper (ACTIVE)
- `nat-rag-workflow.yml` - Main workflow (ACTIVE)
- `nat-rag-integration-fixed.py` - Fixed integration script
- `nat-rag-integration.py` - Integration script
- `nat_llm_client_registration.py` - LLM client registration
- `custom_rag_tool.py` - Custom RAG tool
- `register_custom_tool.py` - Tool registration

### **Active Deployment Files**
- `aira-instruct-llm-deployment.yaml` - AI-Q LLM deployment
- `nim-aiq-deployment.yaml` - NeMo AI-Q deployment
- `rag-server-nodeport.yaml` - RAG server NodePort
- `milvus-external-access.yaml` - Milvus external access
- `milvus-loadbalancer.yaml` - Milvus load balancer
- `milvus-nodeport.yaml` - Milvus NodePort

### **Core Directories**
- `charts/` - Helm charts (KEEP)
- `playbooks/` - Ansible playbooks (KEEP)
- `docs/` - Documentation (KEEP)
- `config/` - Configuration files (KEEP)
- `utils/` - Utility scripts (KEEP)
- `scripts/` - Scripts directory (KEEP)
- `templates/` - Template files (KEEP)

---

## 🟡 **ARCHIVE - Test & Experimental Files**

### **Test Files (Move to archive/)**
- `test-*.yaml` - All test files
- `test-*.py` - All test Python files
- `test-*.sh` - All test shell scripts
- `dns-test-*.yaml` - DNS test files
- `same-node-test-*.yaml` - Same node test files
- `temp-file-copy-pod.yaml` - Temporary file copy

### **Experimental/Iterative Files**
- `final-*.yaml` - Final test iterations
- `simple-*.yaml` - Simple test configurations
- `working-*.yaml` - Working test configurations
- `*-test.yaml` - Test configurations
- `*-working.yaml` - Working test configurations

### **One-off Scripts & Utilities**
- `check-*.yaml` - Check scripts
- `count-*.yaml` - Count utilities
- `delete-*.yaml` - Delete utilities
- `get-*.yaml` - Get utilities
- `live-*.yaml` - Live monitoring
- `purge-collections.py` - Collection purging
- `milvus_test.py` - Milvus testing
- `test_milvus.py` - Milvus testing

### **Ingestion Test Files**
- `ingest-*.yaml` - Ingestion test files
- `import-*.yaml` - Import test files
- `reingest-*.yaml` - Re-ingestion files
- `e2e-*.yaml` - End-to-end tests

### **Configuration Test Files**
- `enable-*.yaml` - Enable test configurations
- `fix-*.yaml` - Fix configurations
- `clear-*.yaml` - Clear configurations
- `discover-*.yaml` - Discovery configurations

---

## 🔴 **ARCHIVE - Obsolete/Deprecated Files**

### **Old Deployment Files**
- `*-deployment.yaml` - Old deployment files
- `*-values.yaml` - Old values files
- `*-nodeport.yaml` - Old NodePort files
- `*-loadbalancer.yaml` - Old load balancer files

### **Redis/Storage Test Files**
- `redis-*.yaml` - Redis test files
- `*-redis-*.yaml` - Redis related files

### **GPU/Performance Test Files**
- `gpu-*.yaml` - GPU test files
- `triton-*.yaml` - Triton test files
- `nim-perf-*.md` - Performance guides

### **Network Test Files**
- `host-network-test.yaml` - Network testing
- `netadmin-*.yaml` - Network admin files

---

## 📁 **Archive Structure Recommendation**

```
archive/
├── tests/                    # All test files
│   ├── test-*.yaml
│   ├── test-*.py
│   ├── test-*.sh
│   └── dns-test-*.yaml
├── experiments/              # Experimental files
│   ├── final-*.yaml
│   ├── simple-*.yaml
│   ├── working-*.yaml
│   └── ingest-*.yaml
├── utilities/                # Utility scripts
│   ├── check-*.yaml
│   ├── count-*.yaml
│   ├── delete-*.yaml
│   └── get-*.yaml
├── deprecated/               # Deprecated files
│   ├── old-deployments/
│   ├── redis-tests/
│   └── gpu-tests/
└── documentation/            # Old docs
    ├── nim-perf-*.md
    └── integration-guides/
```

---

## 🎯 **Cleanup Actions**

### **Phase 1: Move Test Files**
```bash
# Create archive structure
mkdir -p archive/{tests,experiments,utilities,deprecated,documentation}

# Move test files
mv test-*.yaml archive/tests/
mv test-*.py archive/tests/
mv test-*.sh archive/tests/
mv dns-test-*.yaml archive/tests/
```

### **Phase 2: Move Experimental Files**
```bash
# Move experimental files
mv final-*.yaml archive/experiments/
mv simple-*.yaml archive/experiments/
mv working-*.yaml archive/experiments/
mv ingest-*.yaml archive/experiments/
```

### **Phase 3: Move Utility Files**
```bash
# Move utility files
mv check-*.yaml archive/utilities/
mv count-*.yaml archive/utilities/
mv delete-*.yaml archive/utilities/
mv get-*.yaml archive/utilities/
mv clear-*.yaml archive/utilities/
mv discover-*.yaml archive/utilities/
```

### **Phase 4: Move Deprecated Files**
```bash
# Move deprecated files
mv *-deployment.yaml archive/deprecated/ 2>/dev/null || true
mv *-values.yaml archive/deprecated/ 2>/dev/null || true
mv redis-*.yaml archive/deprecated/
mv gpu-*.yaml archive/deprecated/
mv triton-*.yaml archive/deprecated/
```

---

## 📊 **Impact Analysis**

### **Files to Archive:** ~80+ files
### **Files to Keep:** ~20+ core files
### **Space Savings:** Significant reduction in root directory clutter
### **Maintainability:** Much cleaner repository structure

---

## ✅ **Recommended Next Steps**

1. **Review this analysis** - Confirm file classifications
2. **Create archive structure** - Set up organized archive directories
3. **Move files in phases** - Systematic cleanup approach
4. **Update documentation** - Reflect new structure
5. **Test system** - Ensure no broken references
6. **Commit changes** - Version control the cleanup

---

*This analysis was generated automatically based on file patterns, names, and usage analysis.*
