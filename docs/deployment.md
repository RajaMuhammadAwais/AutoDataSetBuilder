# Deployment Guide

This guide covers deploying AutoDataSetBuilder to various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose](#docker-compose)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rajamuhammadawais1/AutoDataSetBuilder.git
   cd AutoDataSetBuilder
   ```

2. **Install dependencies:**
   ```bash
   pip install poetry
   poetry install
   ```

3. **Start infrastructure:**
   ```bash
   docker-compose up -d
   ```

4. **Verify services:**
   ```bash
   # MinIO: http://localhost:9001 (admin/minioadmin)
   # PostgreSQL: localhost:5432
   # Label Studio: http://localhost:8080
   ```

5. **Run demo:**
   ```bash
   cd examples
   bash run_demo.sh
   ```

---

## Docker Compose

The provided `docker-compose.yml` sets up the complete development stack.

### Services

```yaml
Services:
- minio:9000/9001 (S3-compatible storage)
- postgres:5432 (Metadata database)
- label-studio:8080 (Labeling interface)
```

### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v

# Restart specific service
docker-compose restart postgres
```

### Environment Configuration

Create a `.env` file for configuration:

```env
# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_DEFAULT_BUCKETS=raw,processed,shards

# PostgreSQL
POSTGRES_USER=autods_user
POSTGRES_PASSWORD=autods_password
POSTGRES_DB=autods_db

# Label Studio
LABEL_STUDIO_SECRET_KEY=your_secret_key_here

# Application
LOG_LEVEL=INFO
DEBUG=False
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Container registry access
- PersistentVolume provisioner

### Setup

1. **Create namespace:**
   ```bash
   kubectl create namespace autods
   ```

2. **Create secrets:**
   ```bash
   kubectl create secret generic autods-secrets \
     --from-literal=db-password=your_db_password \
     --from-literal=s3-access-key=your_access_key \
     --from-literal=s3-secret-key=your_secret_key \
     -n autods
   ```

3. **Create ConfigMap:**
   ```bash
   kubectl create configmap autods-config \
     --from-literal=db-host=postgres \
     --from-literal=db-port=5432 \
     --from-literal=s3-endpoint=minio:9000 \
     -n autods
   ```

### Deployment Manifest

Create `k8s/deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autods

---
# PostgreSQL StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: autods
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: autods_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: autods-secrets
              key: db-password
        - name: POSTGRES_DB
          value: autods_db
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi

---
# MinIO StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: minio
  namespace: autods
spec:
  serviceName: minio
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        args: ["server", "/data"]
        ports:
        - containerPort: 9000
        - containerPort: 9001
        env:
        - name: MINIO_ROOT_USER
          value: minioadmin
        - name: MINIO_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: autods-secrets
              key: s3-secret-key
        volumeMounts:
        - name: minio-data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: minio-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi

---
# Ingest Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autods-ingest
  namespace: autods
spec:
  replicas: 2
  selector:
    matchLabels:
      app: autods-ingest
  template:
    metadata:
      labels:
        app: autods-ingest
    spec:
      containers:
      - name: ingest
        image: ghcr.io/rajamuhammadawais1/AutoDataSetBuilder/ingest:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DB_URL
          value: postgresql://autods_user:password@postgres:5432/autods_db
        - name: S3_ENDPOINT_URL
          valueFrom:
            configMapKeyRef:
              name: autods-config
              key: s3-endpoint
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
# Service for Ingest
apiVersion: v1
kind: Service
metadata:
  name: autods-ingest
  namespace: autods
spec:
  selector:
    app: autods-ingest
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000

---
# Preprocess Workers Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autods-preprocess
  namespace: autods
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autods-preprocess
  template:
    metadata:
      labels:
        app: autods-preprocess
    spec:
      containers:
      - name: preprocess
        image: ghcr.io/rajamuhammadawais1/AutoDataSetBuilder/preprocess:latest
        imagePullPolicy: Always
        env:
        - name: WORKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"

---
# HPA for Preprocess Workers
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: autods-preprocess-hpa
  namespace: autods
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: autods-preprocess
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Apply manifest
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n autods
kubectl get services -n autods

# View logs
kubectl logs -f deployment/autods-ingest -n autods

# Access services
kubectl port-forward svc/postgres 5432:5432 -n autods
kubectl port-forward svc/minio 9000:9000 -n autods
```

---

## Cloud Deployment

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster --name autods --region us-east-1

# Install metrics server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Deploy RDS (for production PostgreSQL)
# Use AWS RDS console or CLI

# Deploy to cluster
kubectl apply -f k8s/deployment.yaml

# Configure S3 for object storage
aws s3 mb s3://autods-data-prod
```

### Google Cloud GKE

```bash
# Create GKE cluster
gcloud container clusters create autods \
  --zone us-central1-a \
  --num-nodes 3

# Get credentials
gcloud container clusters get-credentials autods --zone us-central1-a

# Deploy
kubectl apply -f k8s/deployment.yaml
```

### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group autods-rg \
  --name autods-aks \
  --node-count 3

# Get credentials
az aks get-credentials --resource-group autods-rg --name autods-aks

# Deploy
kubectl apply -f k8s/deployment.yaml
```

---

## Monitoring & Logging

### Prometheus Monitoring

Create `k8s/prometheus.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: autods
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'autods-services'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - autods
```

### ELK Stack Logging

```bash
# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch -n autods

# Install Kibana
helm install kibana elastic/kibana -n autods

# Install Filebeat
helm install filebeat elastic/filebeat -n autods
```

### Grafana Dashboards

```bash
# Install Grafana
helm install grafana grafana/grafana -n autods

# Port forward
kubectl port-forward svc/grafana 3000:80 -n autods

# Access: http://localhost:3000 (admin/admin)
```

---

## Troubleshooting

### Common Issues

**Service Connection Errors**
```bash
# Check service discovery
kubectl get svc -n autods

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -n autods
nslookup postgres
```

**Database Connection Issues**
```bash
# Check PostgreSQL logs
kubectl logs postgres-0 -n autods

# Connect to database
kubectl run psql --image=postgres -it --rm -n autods -- \
  psql -h postgres -U autods_user -d autods_db
```

**Storage Issues**
```bash
# Check PV/PVC status
kubectl get pvc -n autods
kubectl get pv

# Describe PVC for details
kubectl describe pvc postgres-data-postgres-0 -n autods
```

**Resource Constraints**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n autods

# Check resource requests/limits
kubectl describe deployment autods-ingest -n autods
```

### Debugging

```bash
# Get detailed pod events
kubectl describe pod <pod-name> -n autods

# Stream logs
kubectl logs -f <pod-name> -n autods

# Interactive shell
kubectl exec -it <pod-name> -n autods -- /bin/bash

# Port forward for debugging
kubectl port-forward pod/<pod-name> 8000:8000 -n autods
```

---

## Health Checks

Verify deployment health:

```bash
#!/bin/bash

echo "Checking Kubernetes cluster..."
kubectl cluster-info

echo "Checking namespaces..."
kubectl get ns | grep autods

echo "Checking pods..."
kubectl get pods -n autods

echo "Checking services..."
kubectl get svc -n autods

echo "Checking storage..."
kubectl get pvc -n autods

echo "Checking deployments..."
kubectl get deployments -n autods

echo "All checks complete!"
```

---

## Rollback Procedures

```bash
# View rollout history
kubectl rollout history deployment/autods-ingest -n autods

# Rollback to previous version
kubectl rollout undo deployment/autods-ingest -n autods

# Rollback to specific revision
kubectl rollout undo deployment/autods-ingest --to-revision=2 -n autods

# Check rollout status
kubectl rollout status deployment/autods-ingest -n autods
```

---

## Production Checklist

- [ ] Kubernetes cluster configured and healthy
- [ ] Persistent volumes configured
- [ ] Database backups scheduled
- [ ] Object storage (S3) configured
- [ ] TLS certificates configured
- [ ] Network policies configured
- [ ] RBAC policies configured
- [ ] Monitoring and logging enabled
- [ ] Alerting configured
- [ ] Disaster recovery plan in place
- [ ] Documentation updated
- [ ] Team trained on operations

---

For more information, see:
- [Architecture Guide](architecture.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
