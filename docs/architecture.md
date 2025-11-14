# AutoDataSetBuilder - Architecture Guide

**Created by Raja Muhammad Awais**

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Infrastructure Stack](#infrastructure-stack)
5. [Deployment Architecture](#deployment-architecture)
6. [Design Patterns](#design-patterns)
7. [Scalability Considerations](#scalability-considerations)

---

## System Overview

AutoDataSetBuilder is a modular, distributed system for building high-quality multimodal datasets. The architecture follows a microservices pattern with a shared SDK core.

### Key Principles
- **Modularity** - Each component can be used independently or together
- **Scalability** - Horizontal scaling at multiple levels
- **Fault Tolerance** - Graceful handling of failures
- **Extensibility** - Easy to add new processors and labeling functions

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                                │
│  (Python SDK / REST APIs / Airflow DAGs / CLI Tools)          │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                  SERVICE LAYER                                  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   INGEST     │  │  PREPROCESS  │  │   LABELING   │         │
│  │   SERVICE    │  │   WORKERS    │  │   SERVICE    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
│  ┌──────▼──────────────────▼─────────────────▼──────┐          │
│  │        SHARED SDK (autods package)               │          │
│  │  - ingest.py  - preprocess.py  - labeling.py    │          │
│  │  - shard.py   - utils.py                        │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │   SHARDER    │  │    AIRFLOW   │                           │
│  │   SERVICE    │  │     DAGS     │                           │
│  └──────┬───────┘  └──────────────┘                           │
│         │                                                      │
└────────────────┬──────────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────────┐
│              DATA & METADATA LAYER                             │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   MinIO      │  │  PostgreSQL  │  │ Label Studio │        │
│  │ (S3-like)    │  │              │  │ (Interactive)│        │
│  │ Object Store │  │   Metadata   │  │  Labeling   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │   Redis      │  │  Elasticsearch│                          │
│  │   Cache      │  │   (Optional)   │                          │
│  └──────────────┘  └──────────────┘                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Ingestion Service

**Purpose:** Fetch, validate, and store raw data

**Responsibilities:**
- Retrieve data from URLs, APIs, databases
- Validate integrity and format
- Detect and skip duplicates via checksums
- Store in S3 object storage
- Track metadata in database

**Technology Stack:**
- Language: Python 3.10+
- HTTP: `requests`
- Object Storage: `boto3` (MinIO/S3)
- Database: `psycopg2` (PostgreSQL)

**Key Classes:**
```python
class IngestClient:
    def ingest_url(url: str, license: str, source: str) -> dict
    def ingest_batch(urls: List[str], ...) -> List[dict]
    def validate_asset(asset_bytes: bytes) -> bool
    def close()
```

**Database Schema:**
```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    source_url TEXT,
    s3_key TEXT,
    checksum TEXT UNIQUE,
    license TEXT,
    source TEXT,
    created_at TIMESTAMP,
    status ENUM('ingested', 'processing', 'labeled')
);
```

### 2. Preprocessing Service

**Purpose:** Extract features and preprocess raw data

**Responsibilities:**
- Extract perceptual hashes (pHash) for deduplication
- Generate embeddings (CLIP, ResNet, etc.)
- Normalize and resize images
- Compute metadata statistics
- Support multiple modalities

**Technology Stack:**
- Core: `Pillow`, `imagehash`
- ML: `torch`, `transformers` (optional)
- Async: `asyncio`, `multiprocessing`

**Key Functions:**
```python
def preprocess_asset(
    asset_id: str,
    asset_bytes: bytes,
    modality: str = "image"
) -> dict

def extract_pHash(image_bytes: bytes) -> str

def extract_clip_embedding(
    image_bytes: bytes,
    model: str = "ViT-B/32"
) -> List[float]
```

**Output Features:**
```json
{
    "id": "uuid-123",
    "modality": "image",
    "phash": "a1b2c3d4e5f6g7h8",
    "clip_embedding": [0.123, 0.456, ...],
    "dimensions": {"width": 640, "height": 480},
    "file_size": 245123,
    "format": "jpg",
    "metadata": {}
}
```

### 3. Labeling Service

**Purpose:** Apply weak supervision and aggregate labels

**Responsibilities:**
- Implement labeling functions (LFs)
- Run LabelModel for label aggregation
- Generate probabilistic labels
- Integrate with Label Studio
- Track label quality metrics

**Technology Stack:**
- Framework: `snorkel`
- Data: `pandas`
- Visualization: `matplotlib`, `plotly`

**Key Labeling Functions:**
```python
def lf_caption_has_animal(row) -> Label
    """Check if caption mentions animals"""

def lf_caption_is_short(row) -> Label
    """Check if caption is concise (<50 chars)"""

def lf_image_contains_people(row) -> Label
    """Check if image has detected faces"""
```

**Label Model Pipeline:**
```python
# 1. Create label matrix from LFs
L = np.array([lf(row) for lf in labeling_functions])

# 2. Initialize and fit model
label_model = LabelModel(cardinality=2)
label_model.fit(L, n_epochs=100)

# 3. Get probabilistic labels
prob_labels = label_model.predict_proba(L)
```

### 4. Sharding Service

**Purpose:** Create efficient training datasets

**Responsibilities:**
- Group samples into shards
- Create WebDataset TAR archives
- Optimize for distributed training
- Support versioning and distribution
- Generate metadata indices

**Technology Stack:**
- Format: `webdataset`
- Compression: `tarfile`
- Distribution: `boto3` to S3

**Shard Creation:**
```python
def create_shards(
    samples: Iterator[dict],
    shard_path_template: str,
    max_count: int = 1000,
    shuffle: bool = True
):
    """
    Create WebDataset shards from samples
    
    Shard format:
    - dataset-000000.tar
    - dataset-000000.tar.idx (index)
    - dataset-000001.tar
    - ...
    """
```

**Shard Format:**
```
dataset-000000.tar
├── sample-000000.jpg      (image)
├── sample-000000.json     (metadata)
├── sample-000001.jpg      (image)
├── sample-000001.json     (metadata)
└── ...
```

---

## Data Flow

### End-to-End Pipeline Flow

```
1. INGESTION PHASE
┌─────────────────────────────────────┐
│ Raw Data Sources                    │
│ • Web URLs                          │
│ • APIs                              │
│ • Databases                         │
│ • Local files                       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ IngestClient.ingest_url()           │
│ • Fetch & validate                  │
│ • Compute checksum                  │
│ • Deduplication check               │
│ • Store to S3                       │
│ • Record metadata                   │
└────────────┬────────────────────────┘
             │
             ▼
    PostgreSQL (assets table)
         MinIO (raw bucket)

2. PREPROCESSING PHASE
┌─────────────────────────────────────┐
│ Raw Assets from S3                  │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Preprocess Workers (parallel)        │
│ • Download from S3                   │
│ • Extract pHash                      │
│ • Generate embeddings                │
│ • Compute features                   │
│ • Store processed data               │
└────────────┬─────────────────────────┘
             │
             ▼
    PostgreSQL (features table)
         MinIO (processed bucket)

3. LABELING PHASE
┌─────────────────────────────────────┐
│ Processed Assets                    │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Labeling Service                    │
│ • Load features                      │
│ • Apply weak LFs                     │
│ • Aggregate with LabelModel          │
│ • Generate prob. labels              │
│ • Option: Send to Label Studio       │
└────────────┬─────────────────────────┘
             │
             ▼
    PostgreSQL (labels table)
         Label Studio (UI)

4. SHARDING PHASE
┌─────────────────────────────────────┐
│ Labeled Samples                     │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Sharder Service                     │
│ • Group by shard                     │
│ • Download samples                   │
│ • Create TAR archives                │
│ • Generate indices                   │
│ • Upload to S3                       │
└────────────┬─────────────────────────┘
             │
             ▼
    MinIO (shards bucket)
         WebDataset ready
```

---

## Infrastructure Stack

### Docker Compose Services

#### MinIO (S3-compatible Object Storage)
```yaml
Service: minio
Port: 9000 (API), 9001 (Console)
Buckets:
  - raw          (ingested data)
  - processed    (feature data)
  - shards       (training datasets)
Credentials: minioadmin/minioadmin
```

**API Usage:**
```python
import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4')
)

# Upload file
s3.upload_file('local.jpg', 'raw', 's3key.jpg')

# Download file
s3.download_file('raw', 's3key.jpg', 'local.jpg')

# List files
response = s3.list_objects_v2(Bucket='raw', Prefix='path/')
```

#### PostgreSQL (Metadata Database)
```yaml
Service: postgres
Port: 5432
Database: autods_db
User: autods_user
Password: autods_password
```

**Tables:**
```sql
-- Assets table
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    checksum TEXT UNIQUE,
    license TEXT,
    source TEXT,
    status ENUM,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Features table
CREATE TABLE features (
    asset_id UUID PRIMARY KEY REFERENCES assets(id),
    phash TEXT UNIQUE,
    clip_embedding VECTOR(512),
    file_size INTEGER,
    dimensions JSONB,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Labels table
CREATE TABLE labels (
    asset_id UUID PRIMARY KEY REFERENCES assets(id),
    label INTEGER,
    probability FLOAT,
    labeled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    label_function TEXT
);
```

#### Label Studio (Interactive Labeling)
```yaml
Service: label-studio
Port: 8080
URL: http://localhost:8080
Secret: insecure_dev_key (development only)
```

**Features:**
- Web-based annotation interface
- Support for images, text, audio
- Team collaboration
- Quality metrics and inter-annotator agreement

---

## Deployment Architecture

### Development Environment
```
Local Machine / Dev Container
├── docker-compose up (MinIO, PostgreSQL, Label Studio)
├── Python SDK (poetry install)
├── Jupyter notebooks for exploration
└── Local testing
```

### Production Kubernetes Deployment
```
Kubernetes Cluster
├── Namespace: autods
├── Ingest Service
│   ├── Deployment (replicas: 2+)
│   ├── Service (LoadBalancer)
│   └── ConfigMap (credentials)
├── Preprocess Workers
│   ├── StatefulSet (GPU nodes)
│   ├── HPA (auto-scale)
│   └── Job Queue (optional: Celery)
├── Labeling Service
│   ├── Deployment (replicas: 1-2)
│   ├── Service (ClusterIP)
│   └── PersistentVolume (cache)
└── Sharder Service
    ├── Job (batch)
    ├── CronJob (periodic)
    └── ServiceAccount (S3 access)

External Services
├── Cloud Storage (AWS S3 / GCS)
├── Database (RDS PostgreSQL)
├── Cache (ElastiCache Redis)
└── Message Queue (SQS / Kafka)
```

### CI/CD Pipeline
```
GitHub Repository
├── Trigger: Push / PR
├── GitHub Actions Workflow
│   ├── Lint & Format Check
│   │   ├── black
│   │   ├── flake8
│   │   └── mypy
│   ├── Test Suite
│   │   ├── Unit tests
│   │   ├── Integration tests
│   │   └── Coverage report
│   ├── Build Docker Images
│   │   ├── Build images
│   │   └── Push to registry
│   ├── Deploy to Staging
│   │   ├── Update manifests
│   │   └── Run smoke tests
│   └── Deploy to Production
│       ├── Canary deployment
│       └── Health checks
└── Artifacts
    ├── Coverage reports
    ├── Docker images
    └── Release packages
```

---

## Design Patterns

### 1. Service Pattern
Each component is a standalone service that can be:
- Deployed independently
- Scaled horizontally
- Replaced with alternatives

### 2. Data Pipeline Pattern
```python
# Linear pipeline with error handling
class Pipeline:
    def __init__(self):
        self.stages = []
    
    def add_stage(self, stage):
        self.stages.append(stage)
    
    def execute(self, input_data):
        data = input_data
        for stage in self.stages:
            try:
                data = stage.process(data)
            except Exception as e:
                logger.error(f"Stage failed: {stage}")
                handle_error(data, e)
        return data
```

### 3. Factory Pattern
```python
class ProcessorFactory:
    @staticmethod
    def create_processor(modality: str):
        if modality == "image":
            return ImageProcessor()
        elif modality == "text":
            return TextProcessor()
        else:
            raise ValueError(f"Unknown modality: {modality}")
```

### 4. Strategy Pattern
```python
class Labeler:
    def __init__(self, strategy: LabelingStrategy):
        self.strategy = strategy
    
    def label(self, data):
        return self.strategy.label(data)

# Different strategies
class SnokelStrategy(LabelingStrategy): ...
class RuleBasedStrategy(LabelingStrategy): ...
class DistantSupervisionStrategy(LabelingStrategy): ...
```

---

## Scalability Considerations

### Horizontal Scaling

**Ingestion Service:**
- Multi-instance deployment
- Load balancer distribution
- S3 handles concurrent uploads
- Database connection pooling

**Preprocessing Workers:**
- Autoscaling based on queue depth
- GPU node allocation
- Batch processing for efficiency
- Distributed feature store (optional: Redis)

**Labeling Service:**
- Stateless design for scaling
- Cached label functions
- Distributed LabelModel training

### Performance Optimization

**1. Caching Strategy**
```python
@cache(ttl=3600)
def get_features(asset_id):
    return database.query(...)

# Cache layers:
# - Redis (hot data)
# - PostgreSQL (persistent)
# - S3 (cold data)
```

**2. Batch Processing**
```python
# Process multiple assets efficiently
def batch_preprocess(asset_ids, batch_size=100):
    for batch in chunks(asset_ids, batch_size):
        features = parallel_process(batch)
        save_batch(features)
```

**3. Lazy Loading**
```python
# Don't load everything into memory
class LargeDataset:
    def __iter__(self):
        for record in database.stream():
            yield record
```

### Database Optimization

```sql
-- Indexing strategy
CREATE INDEX idx_assets_checksum ON assets(checksum);
CREATE INDEX idx_features_phash ON features(phash);
CREATE INDEX idx_labels_asset ON labels(asset_id);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_created ON assets(created_at);

-- Partitioning (optional, for very large tables)
CREATE TABLE assets_2024_q1 PARTITION OF assets
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

---

## Security Considerations

### Authentication & Authorization
- Service-to-service: API keys, OAuth2
- Database: Role-based access control
- S3: IAM policies, bucket policies
- Label Studio: User management, teams

### Data Protection
- Encryption at rest: S3 server-side encryption
- Encryption in transit: TLS 1.2+
- Secrets management: HashiCorp Vault / AWS Secrets Manager
- Data anonymization: PII removal pipeline

### Compliance
- Data retention policies
- Audit logging (CloudTrail / custom)
- GDPR compliance: Right to be forgotten
- License tracking for data

---

## Monitoring & Observability

### Metrics to Track
- **Throughput**: items ingested/processed/labeled per hour
- **Latency**: end-to-end pipeline time
- **Error rates**: by component and error type
- **Resource utilization**: CPU, memory, storage
- **Data quality**: deduplication rate, label confidence

### Logging Strategy
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Ingesting asset: {asset_id}")
logger.warning(f"Duplicate detected: {checksum}")
logger.error(f"Failed to preprocess: {asset_id}", exc_info=True)
```

### Alerting
- Queue depth warnings (backing up)
- Error rate thresholds
- Low label confidence alerts
- Storage quota approaching
- Database performance degradation

---

## Future Enhancements

1. **Distributed Training** - Integration with distributed ML frameworks
2. **Active Learning** - Query strategy for efficient labeling
3. **Version Control** - Data versioning and lineage tracking
4. **AutoML** - Automatic feature engineering
5. **Real-time Processing** - Streaming pipeline support
6. **Multi-region Deployment** - Global distribution
7. **Advanced Analytics** - Dataset statistics and visualization

---

## References

- [Snorkel Documentation](https://snorkel.org/)
- [WebDataset](https://github.com/webdataset/webdataset)
- [Label Studio](https://labelstud.io/)
- [MinIO Documentation](https://docs.min.io/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
