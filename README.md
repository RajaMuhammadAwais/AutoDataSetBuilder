# AutoDataSetBuilder 🚀

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub Workflow Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions)](/.github/workflows/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen?style=flat-square)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen?style=flat-square)](https://github.com/rajamuhammadawais1/AutoDataSetBuilder)

**A modular, production-ready framework for building high-quality multimodal datasets at scale**

[Documentation](#-documentation) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Components](#-components)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

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

```
┌─────────────────────────────────────────────────────────────┐
│                     AutoDataSetBuilder                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   INGEST     │  │  PREPROCESS  │  │   LABELING   │     │
│  │              │  │              │  │              │     │
│  │ • URL Fetch  │  │ • pHash      │  │ • Snorkel    │     │
│  │ • S3 Upload  │  │ • CLIP Embed │  │ • Weak Label │     │
│  │ • Validation │  │ • Features   │  │ • LabelStudio│     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │    SHARDING     │                       │
│                  │                 │                       │
│                  │ • WebDataset    │                       │
│                  │ • TAR Creation  │                       │
│                  │ • Distribution  │                       │
│                  └────────┬────────┘                       │
│                           │                                │
├───────────────────────────┼────────────────────────────────┤
│                    INFRASTRUCTURE                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   MinIO      │  │  PostgreSQL  │  │ Label Studio │     │
│  │              │  │              │  │              │     │
│  │ Object Store │  │   Metadata   │  │  Interactive │     │
│  │   (S3-like)  │  │   Database   │  │   Labeling   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

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
