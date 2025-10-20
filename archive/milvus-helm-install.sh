#!/bin/bash

# Install Milvus using Helm
echo "Installing Milvus using Helm..."

# Add Milvus Helm repository
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo update

# Install Milvus with custom values
helm install milvus milvus/milvus \
  --namespace default \
  --set standalone.persistence.enabled=true \
  --set standalone.persistence.existingClaim=blueprint-storage \
  --set standalone.resources.requests.memory=2Gi \
  --set standalone.resources.requests.cpu=1 \
  --set standalone.resources.limits.memory=4Gi \
  --set standalone.resources.limits.cpu=2 \
  --set etcd.persistence.enabled=true \
  --set etcd.persistence.existingClaim=blueprint-storage \
  --set minio.persistence.enabled=true \
  --set minio.persistence.existingClaim=blueprint-storage

echo "Milvus installation completed!"
