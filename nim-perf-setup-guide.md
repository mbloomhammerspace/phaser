# NIM Perf Setup Guide

## 📁 Directory Structure

The deployment creates the following directory structure on the NFS mount (`/nim-perf-data/`):

```
/nim-perf-data/
├── models/          # NIM model files and configurations
├── configs/         # Test configurations and input data
├── results/         # Performance test results
└── logs/           # Performance logs and metrics
```

## 🚀 Deployment

Deploy the Triton Inference Server with genai-perf:

```bash
kubectl apply -f triton-genai-perf-deployment.yaml
```

## 📊 Access Points

- **HTTP API**: `http://localhost:30800`
- **gRPC API**: `localhost:30801`
- **Metrics**: `http://localhost:30802/metrics`

## 📁 File Organization

### Models Directory (`/nim-perf-data/models/`)
Place your NIM model files here:
- Model weights and configurations
- Custom model definitions
- Model metadata files

### Configs Directory (`/nim-perf-data/configs/`)
Store test configurations:
- `test_config.json` - Default test configuration
- Custom test scenarios
- Input data files
- Benchmark configurations

### Results Directory (`/nim-perf-data/results/`)
Performance test results:
- `nim_perf_results.json` - Default results file
- CSV exports
- Performance reports
- Comparison data

### Logs Directory (`/nim-perf-data/logs/`)
Performance logs:
- Triton server logs
- genai-perf execution logs
- System metrics
- Error logs

## 🧪 Running Custom Tests

1. **Create custom configuration**:
```bash
kubectl exec -it <pod-name> -- bash
# Edit /nim-perf-data/configs/my_test.json
```

2. **Run custom test**:
```bash
genai-perf -m your_model -u localhost:8000 -i grpc \
  --input-data /nim-perf-data/configs/my_test.json \
  --results-file /nim-perf-data/results/my_results.json
```

## 📈 Key Metrics

genai-perf measures:
- **Tokens per Second (TPS)**
- **Time to First Token (TTFT)**
- **Latency percentiles (P50, P95, P99)**
- **Throughput under load**
- **Concurrent request handling**

## 🔧 Customization

### Model Configuration
Edit `/nim-perf-data/models/` to add your specific NIM models.

### Test Parameters
Modify `/nim-perf-data/configs/test_config.json`:
- `concurrency`: Number of concurrent requests
- `sequence_length`: Input sequence length
- `max_tokens`: Maximum tokens to generate
- `measurement_requests`: Number of measurement requests

### Results Analysis
Results are saved in JSON format with detailed metrics for analysis.
