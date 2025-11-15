# AutoDataSetBuilder

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Lint%20%2F%20Type-blue?style=flat-square)](.github/workflows/)
[![Tests](https://img.shields.io/badge/Tests-Unit%20%2F%20Integration-green?style=flat-square)](.github/workflows/)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen?style=flat-square)](https://github.com/rajamuhammadawais1/AutoDataSetBuilder)

**Build high-quality multimodal datasets at scale with an intuitive, modular Python framework**

[About](#about) • [Getting Started](#getting-started) • [Usage](#usage) • [Architecture](#architecture) • [Contributing](#contributing) • [Docs](#documentation)

</div>

---

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Example 1: Python SDK](#example-1-ingesting-and-preprocessing-data-with-the-python-sdk)
  - [Example 2: Running Services](#example-2-running-services-with-docker-compose)
  - [Example 3: Airflow DAGs](#example-3-orchestrating-with-airflow-dags)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

---

## About

**AutoDataSetBuilder** is a production-ready framework for building, processing, and managing multimodal datasets. Whether you're an ML researcher, data engineer, or team building data pipelines, AutoDataSetBuilder provides:

- **Modular Components**: Ingest, preprocess, label, and shard data independently or as a unified pipeline
- **Multimodal Support**: Handle images, text, audio, and mixed-modality datasets seamlessly
- **Scalable Architecture**: From local development to cloud deployments with Kubernetes
- **Developer-Friendly SDK**: Pure Python API with clear, documented classes and functions
- **Production-Ready**: Error handling, monitoring, metrics, and orchestration built-in
- **Extensible Design**: Add custom labeling functions, preprocessing steps, and data sources

### High-Level Mission

AutoDataSetBuilder aims to **democratize dataset creation** by providing:
1. A clear, well-documented pipeline from raw data to training-ready shards
2. Flexible, composable components for different use cases
3. Production infrastructure (monitoring, error handling, scalability) without the complexity
4. A shared ecosystem for dataset builders to collaborate

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🔌 **Modular SDK** | Ingest, preprocess, label, and shard independently or together |
| 📊 **Multimodal** | Native support for images, text, audio, and custom data types |
| 🏷️ **Intelligent Labeling** | Snorkel weak supervision with label models and aggregation |
| ⚡ **Scalable Processing** | Distributed preprocessing workers, parallel API calls, batch operations |
| 🗄️ **Efficient Sharding** | WebDataset-compatible TAR shards optimized for training |
| 🐳 **Docker & Compose** | Fully containerized local dev environment, multi-service orchestration |
| 🔄 **Airflow Integration** | Production-grade DAGs with retries, monitoring, and failure notifications |
| 📈 **Human-in-the-Loop** | Label Studio integration for interactive data annotation |
| ☁️ **Cloud Native** | S3-compatible storage (MinIO), Kubernetes-ready, multi-cloud support |
| 🔐 **Secure** | Environment-based secrets, no hardcoded credentials, audit logging |

---

## Getting Started

### Prerequisites

- **Python**: 3.10 or later
- **Docker & Docker Compose**: For running services locally
- **Git**: For cloning the repository
- **Poetry** (optional): For dependency management

### Installation

#### Option 1: Using Docker Compose (Recommended for Quick Start)

1. Clone the repository:
```bash
git clone https://github.com/rajamuhammadawais1/AutoDataSetBuilder.git
cd AutoDataSetBuilder
```

2. Start all services:
```bash
docker-compose up -d
```

3. Verify services are running:
```bash
docker-compose ps
# Expected output:
# NAME              SERVICE                    STATUS
# autods-minio      minio                      Up
# autods-postgres   postgres                   Up
# autods-label-studio  label-studio            Up
```

4. Access services:
- **MinIO Console**: http://localhost:9001 (user: `minioadmin`, password: `minioadmin`)
- **Label Studio**: http://localhost:8080
- **PostgreSQL**: `postgresql://autods_user:autods_password@localhost:5432/autods_db`

#### Option 2: Using pip (For SDK Only)

```bash
# Install from source
pip install -e .

# Or install from PyPI (when available)
pip install auto-dataset-builder
```

#### Option 3: Using Poetry (For Development)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Configuration

Set environment variables before running (or create a `.env` file):

```bash
# S3/MinIO Configuration
export S3_ENDPOINT_URL="http://localhost:9000"
export MINIO_ROOT_USER="minioadmin"
export MINIO_ROOT_PASSWORD="minioadmin"

# Database Configuration
export DB_URL="postgresql://autods_user:autods_password@localhost:5432/autods_db"

# Data Buckets
export RAW_BUCKET="raw"
export PROCESSED_BUCKET="processed"
export SHARDS_BUCKET="shards"

# Optional: Airflow Configuration
export AIRFLOW_HOME="/workspace/infra/airflow"
export AIRFLOW__CORE__EXECUTOR="LocalExecutor"

# Optional: Slack Notifications
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Create a `.env` file in the project root:
```bash
cp .env.example .env
# Edit .env with your values
```

---

## Usage

### Example 1: Ingesting and Preprocessing Data with the Python SDK

Ingest images from URLs and extract features:

```python
from autods.ingest import IngestClient
from autods.preprocess import preprocess_asset
import boto3
import os

# Initialize the ingest client
ingest_client = IngestClient(
    s3_bucket="raw",
    db_url=os.getenv("DB_URL")
)

# Ingest a sample image
result = ingest_client.ingest_url(
    url="https://example.com/image.jpg",
    license="cc0",
    source="example"
)

print(f"Ingested asset: {result}")
# Output: {'id': 'uuid', 's3_key': 'raw/abc123...', 'checksum': 'sha256...'}

# Retrieve and preprocess the asset
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD")
)

obj = s3.get_object(Bucket="raw", Key=result['s3_key'])
asset_bytes = obj['Body'].read()

features = preprocess_asset(
    asset_id=result['id'],
    asset_bytes=asset_bytes,
    modality='image'
)

print(f"Features extracted: {features}")
# Output: {'asset_id': 'uuid', 'phash': 'abc123...', 'clip_embedding': [...]}

ingest_client.close()
```

### Example 2: Running Services with Docker Compose

Process a dataset using containerized microservices:

```bash
# 1. Start all services
docker-compose up -d

# 2. Initialize the database
docker exec autods-postgres psql -U autods_user -d autods_db -c \
  "CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY,
    source_url TEXT,
    s3_key TEXT UNIQUE,
    checksum TEXT UNIQUE,
    license TEXT,
    source TEXT,
    created_at TIMESTAMP
  );"

# 3. Run the ingest service (example)
docker-compose exec ingest-service python app.py

# 4. Monitor processing
docker-compose logs -f preprocess-service

# 5. View results in Label Studio
open http://localhost:8080
```

### Example 3: Orchestrating with Airflow DAGs

Schedule a complete pipeline with Airflow:

```bash
# 1. Initialize Airflow
export AIRFLOW_HOME=$(pwd)/infra/airflow
airflow db init

# 2. Create an admin user
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

# 3. Start Airflow web server and scheduler
airflow webserver -p 8080 &
airflow scheduler &

# 4. Access the UI
open http://localhost:8080

# 5. Trigger the auto_dataset_dag
airflow dags trigger auto_dataset_dag

# 6. Monitor execution
airflow dags list-runs --dag-id auto_dataset_dag
```

For more examples, see the [examples/](examples/) folder.

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                         │
│  Python SDK • REST APIs • Airflow DAGs • CLI Tools      │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                    SERVICE LAYER                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   INGEST     │  │  PREPROCESS  │  │   LABELING   │  │
│  │   SERVICE    │  │   WORKERS    │  │   SERVICE    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                     │                                    │
│         ┌───────────▼────────────┐                      │
│         │   SHARED SDK CORE      │                      │
│         │  (autods package)      │                      │
│         │  - ingest              │                      │
│         │  - preprocess          │                      │
│         │  - labeling            │                      │
│         │  - shard               │                      │
│         └───────────┬────────────┘                      │
│                     │                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  DATA & METADATA LAYER                   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    MinIO     │  │  PostgreSQL  │  │Label Studio  │  │
│  │ (S3-like)    │  │  (Metadata)  │  │ (Interactive)│  │
│  │Object Store  │  │              │  │ Labeling    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Prometheus   │  │   Grafana    │                    │
│  │ (Metrics)    │  │(Dashboards)  │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Data Pipeline Flow

```
Raw Data Sources (URLs, APIs, Files)
           │
           ▼
┌──────────────────────┐
│  INGEST SERVICE      │
│  - Fetch data        │
│  - Validate format   │
│  - Upload to S3      │
│  - Record metadata   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ PREPROCESS WORKERS   │
│  - Extract features  │
│  - Compute hashes    │
│  - Embeddings        │
│  - Deduplication     │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  LABELING SERVICE    │
│  - Apply LFs         │
│  - Aggregate labels  │
│  - Probabilistic     │
│  - Quality metrics   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│   SHARDING SERVICE   │
│  - Group samples     │
│  - Create TAR shards │
│  - Compute indices   │
│  - Distribution      │
└─────────┬────────────┘
          │
          ▼
Training-Ready Dataset
(TAR shards on S3)
```

### Key Components

- **Ingest Service**: Downloads and validates raw data, stores in S3, records metadata
- **Preprocess Workers**: Parallel feature extraction (pHash, CLIP embeddings, deduplication)
- **Labeling Service**: Weak labeling with Snorkel, probabilistic label aggregation
- **Sharding Service**: Creates WebDataset-compatible TAR shards for efficient training
- **Airflow Orchestration**: Schedules and monitors the entire pipeline with retries and error handling
- **MinIO**: S3-compatible object storage for raw, processed, and shard data
- **PostgreSQL**: Stores asset metadata, labels, and pipeline state
- **Label Studio**: Human-in-the-loop annotation interface for data review and correction

For detailed architecture information, see [docs/architecture.md](docs/architecture.md).

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct and guidelines
- Development setup instructions
- Coding conventions and style guide
- Testing requirements
- Pull request process
- Issue reporting guidelines

Quick start for contributors:

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/AutoDataSetBuilder.git
cd AutoDataSetBuilder

# 2. Create a branch
git checkout -b feature/your-feature-name

# 3. Install dev dependencies
poetry install

# 4. Run tests
pytest tests/

# 5. Run linting
black sdk/ services/ tests/
flake8 sdk/ services/ tests/
mypy sdk/ services/

# 6. Commit and push
git push origin feature/your-feature-name

# 7. Create a pull request
```

---

## Documentation

- **[README.md](README.md)** - This file (project overview and quick start)
- **[docs/architecture.md](docs/architecture.md)** - Detailed system architecture, components, and design patterns
- **[docs/deployment.md](docs/deployment.md)** - Deployment guides (Docker, Kubernetes, cloud platforms)
- **[docs/api/](docs/api/)** - SDK API documentation (generated with Sphinx)
- **[examples/](examples/)** - Runnable example scripts and tutorials
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines and development setup

### API Documentation

To generate API documentation:

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Generate HTML docs
cd docs
sphinx-build -b html -a . _build/html

# View docs
open _build/html/index.html
```

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🎯 Overview

AutoDataSetBuilder is an end-to-end framework designed to simplify the process of building high-quality multimodal datasets. It provides modular components for ingesting raw data, preprocessing and extracting features, programmatically labeling data, and creating efficient shards for training.

**Perfect for:**
- ML researchers building custom datasets
- Data engineers creating production pipelines
- Teams implementing human-in-the-loop labeling workflows
- Organizations optimizing dataset storage and distribution

---


## ✨ Key Features

- **🔌 Modular Architecture** - Independent, composable components that work together seamlessly
- **📊 Multimodal Support** - Handle images, text, and mixed-modality data
- **🏷️ Intelligent Labeling** - Programmatic labeling with Snorkel weak supervision
- **⚡ Scalable Processing** - Distributed preprocessing with worker pools
- **🗄️ Efficient Sharding** - WebDataset integration for optimized training data
- **🐳 Docker Ready** - Complete containerized stack with docker-compose
- **🔄 CI/CD Integration** - GitHub Actions workflows for automated testing and deployment
- **📈 Human-in-the-Loop** - Label Studio integration for interactive labeling
- **☁️ Cloud Native** - S3-compatible object storage with MinIO

---

## 🏗️ Architecture

<img width="3120" height="4720" alt="architecture" src="https://github.com/user-attachments/assets/0f696186-6af8-44e9-859a-8fc845e5af7d" />



### Data Flow

```
Raw Data Sources
       │
       ▼
┌──────────────┐
│   INGESTION  │ - Fetch from URLs/APIs
│   SERVICE    │ - Validate & deduplicate
│              │ - Store in S3
└────────┬─────┘
         │
         ▼
┌──────────────┐
│ PREPROCESS   │ - Extract features (pHash, embeddings)
│  WORKERS     │ - Parallel processing
│              │ - Store processed data
└────────┬─────┘
         │
         ▼
┌──────────────┐
│   LABELING   │ - Run weak labeling functions
│   SERVICE    │ - LabelModel aggregation
│              │ - Probabilistic labels
└────────┬─────┘
         │
         ▼
┌──────────────┐
│   SHARDING   │ - Group samples
│   SERVICE    │ - Create TAR shards
│              │ - Distribute for training
└──────────────┘
         │
         ▼
   Training Ready
   Dataset Shards
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/rajamuhammadawais1/AutoDataSetBuilder.git
cd AutoDataSetBuilder
```

2. **Install dependencies:**
```bash
# Using Poetry (recommended)
pip install poetry
poetry install

# Or using pip
pip install -r requirements.txt
```

3. **Start the infrastructure stack:**
```bash
docker-compose up -d
```

4. **Verify services are running:**
```bash
# MinIO Console: http://localhost:9001
# Label Studio: http://localhost:8080
# PostgreSQL: localhost:5432
```

### Running the Demo

```bash
cd examples
bash run_demo.sh
```

This demo will:
1. Ingest a sample image from Wikimedia Commons
2. Preprocess it (extract features)
3. Run programmatic labeling
4. Create a WebDataset shard

---

## 📁 Project Structure

```
AutoDataSetBuilder/
├── sdk/                           # Core SDK
│   └── autods/
│       ├── __init__.py
│       ├── ingest.py             # Data ingestion module
│       ├── preprocess.py         # Feature extraction
│       ├── labeling.py           # Weak supervision & labeling
│       └── shard.py              # Sharding utilities
│
├── services/                      # Microservices
│   ├── ingest_service/           # Ingestion API
│   │   └── app.py
│   ├── labeling_service/         # Labeling API
│   │   └── run_label_model.py
│   ├── preprocess_workers/       # Parallel preprocessing
│   │   └── preprocess.py
│   └── sharder/                  # Sharding service
│       └── create_shards.py
│
├── infra/                         # Infrastructure
│   └── airflow/
│       └── dags/
│           └── auto_dataset_dag.py
│
├── ci/                            # CI/CD Configuration
│   └── pipeline.yml              # GitHub Actions workflow
│
├── docs/                          # Documentation
│   └── architecture.md           # Architecture details
│
├── examples/                      # Example scripts
│   └── run_demo.sh              # End-to-end demo
│
├── docker-compose.yml            # Local development stack
├── pyproject.toml               # Python project config
└── README.md                    # This file
```

---

## 🔧 Components

### 1. **Ingestion Service**
- Fetches data from URLs and APIs
- Validates and deduplicates content
- Stores raw data in S3-compatible object storage
- Tracks metadata in PostgreSQL

**Usage:**
```python
from sdk.autods.ingest import IngestClient

client = IngestClient(s3_bucket="raw", db_url="postgresql://...")
result = client.ingest_url(
    url="https://example.com/image.jpg",
    license="cc0",
    source="external_api"
)
asset_id = result['id']
client.close()
```

### 2. **Preprocessing Service**
- Extracts perceptual hashes (pHash) for deduplication
- Generates ML embeddings (CLIP, etc.)
- Computes derived features
- Supports multiple modalities

**Usage:**
```python
from sdk.autods.preprocess import preprocess_asset

features = preprocess_asset(
    asset_id="uuid-123",
    asset_bytes=image_data,
    modality="image"
)
```

### 3. **Labeling Service**
- Implements weak supervision functions
- Aggregates labels with Snorkel's LabelModel
- Provides probabilistic labels
- Integrates with Label Studio for human-in-the-loop

**Usage:**
```python
from sdk.autods.labeling import run_label_model, lf_caption_has_animal

labeled_df = run_label_model(df, [lf_caption_has_animal])
```

### 4. **Sharding Service**
- Groups samples into efficient shards
- Creates TAR archives compatible with WebDataset
- Optimizes for distributed training
- Supports versioning and distribution

**Usage:**
```python
from services.sharder.create_shards import create_shards

create_shards(
    sample_iterator,
    "./shards/dataset-%06d.tar",
    max_count=1000
)
```

---

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)** - Detailed system architecture and design decisions
- **[API Reference](docs/api.md)** - Complete SDK API documentation
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and contribution guidelines

---

## 🐳 Docker & Compose

The project includes a complete Docker Compose stack for local development:

**Services:**
- **MinIO** - S3-compatible object storage (port 9000, console 9001)
- **PostgreSQL** - Metadata database (port 5432)
- **Label Studio** - Interactive labeling platform (port 8080)

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop services:**
```bash
docker-compose down
```

---

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for automated testing and deployment:

**Workflow Features:**
- ✅ Python linting and type checking
- ✅ Unit and integration tests
- ✅ Code coverage reporting
- ✅ Docker image building and pushing
- ✅ Automated deployment to production

**Workflows:**
- `ci.yml` - Tests on every push and PR
- `release.yml` - Automated releases and Docker builds

**View workflow status:**
- Go to [Actions](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/actions)

---

## 🛠️ Development

### Setup Development Environment

```bash
# Install dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run linting
flake8 sdk/ services/
mypy sdk/ services/

# Format code
black sdk/ services/
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=sdk --cov=services

# Specific test file
pytest tests/test_ingest.py
```

---

## 📦 Dependencies

**Core Dependencies:**
- `requests` - HTTP client for data fetching
- `boto3` - AWS SDK for S3 operations
- `psycopg2-binary` - PostgreSQL adapter
- `pandas` - Data manipulation
- `snorkel` - Weak supervision framework
- `torch` - Deep learning (optional)
- `webdataset` - Efficient dataset format
- `Pillow` - Image processing
- `imagehash` - Perceptual hashing

See `pyproject.toml` for complete dependency list.

---

## 🌟 Use Cases

1. **Computer Vision Datasets** - Build labeled image datasets with deduplication
2. **Multimodal Learning** - Combine images, text, and metadata
3. **Weak Supervision** - Use multiple noisy labels to create training data
4. **Active Learning** - Integrate human-in-the-loop with Label Studio
5. **Data Preprocessing** - Scale feature extraction across millions of samples

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

**Quick steps:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Raja Muhammad Awais** - Creator & Lead Developer

---

## 📧 Support & Contact

- **Issues & Bugs:** [GitHub Issues](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/discussions)
- **Email:** 

---

## 🙏 Acknowledgments

- [Snorkel](https://snorkel.org/) - Weak supervision framework
- [WebDataset](https://github.com/webdataset/webdataset) - Efficient dataset format
- [Label Studio](https://labelstud.io/) - Data labeling platform
- [MinIO](https://min.io/) - S3-compatible storage
- Apache Airflow - Workflow orchestration

---

<div align="center">

**[⬆ back to top](#autodatasetbuilder-)**

Created with ❤️ by **Raja Muhammad Awais** 🚀

</div>
