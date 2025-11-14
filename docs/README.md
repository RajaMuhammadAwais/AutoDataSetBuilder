# AutoDataSetBuilder Documentation

Welcome to the AutoDataSetBuilder documentation! This folder contains comprehensive guides for understanding and using the framework.

## Quick Navigation

### Getting Started
- **[README.md](../README.md)** - Project overview and quick start guide

### Documentation Files

#### [architecture.md](./architecture.md)
Comprehensive system architecture documentation including:
- System overview and design principles
- Component architecture for each service
- Data flow diagrams
- Infrastructure stack setup
- Deployment architecture
- Design patterns used
- Scalability considerations
- Security considerations
- Monitoring and observability strategies

#### [deployment.md](./deployment.md)
Production deployment guide covering:
- Local development setup
- Docker Compose configuration
- Kubernetes deployment
- Cloud platform deployments (AWS, GCP, Azure)
- Monitoring and logging setup
- Troubleshooting guides
- Health checks
- Rollback procedures

#### [api.md](./api.md) *(Coming Soon)*
Complete API reference for all SDK modules:
- IngestClient API
- PreprocessProcessor API
- LabelingModel API
- Sharder API
- Utility functions

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- License information

---

## Architecture Overview

```
┌─────────────────────────────────┐
│       Client Layer              │
│ (SDK / APIs / DAGs / CLI)       │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│      Service Layer              │
│ ┌──────────────────────────┐    │
│ │ Ingest - Preprocess -    │    │
│ │ Labeling - Sharding      │    │
│ └──────────────────────────┘    │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│   Infrastructure Layer          │
│ ┌──────────────────────────┐    │
│ │ MinIO - PostgreSQL -     │    │
│ │ Label Studio             │    │
│ └──────────────────────────┘    │
└─────────────────────────────────┘
```

---

## Key Components

### 1. **Ingestion Service**
Fetches, validates, and stores raw data in S3.

### 2. **Preprocessing Service**
Extracts features (hashes, embeddings) from raw data.

### 3. **Labeling Service**
Applies weak supervision and generates probabilistic labels.

### 4. **Sharding Service**
Creates efficient WebDataset TAR archives for training.

---

## Documentation Structure

```
docs/
├── README.md (this file)
├── architecture.md
├── deployment.md
├── api.md (coming soon)
├── tutorials/ (coming soon)
│   ├── basic-usage.md
│   ├── custom-processors.md
│   └── advanced-labeling.md
└── faq.md (coming soon)
```

---

## Quick Links

- **GitHub Repository**: https://github.com/rajamuhammadawais1/AutoDataSetBuilder
- **Issues & Bugs**: https://github.com/rajamuhammadawais1/AutoDataSetBuilder/issues
- **Discussions**: https://github.com/rajamuhammadawais1/AutoDataSetBuilder/discussions
- **PyPI Package**: https://pypi.org/project/auto-dataset-builder/

---

## Getting Help

### Documentation
1. Check the relevant guide (Architecture, Deployment, etc.)
2. Review example scripts in the `examples/` folder
3. Check the [FAQ](./faq.md) for common questions

### Community
1. Search [existing issues](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/issues)
2. Ask on [GitHub Discussions](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/discussions)
3. Contact via email: support@example.com

### Development
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup
- Join our community for discussions and support

---

## Contributing to Documentation

We welcome documentation improvements! Please:

1. Fork the repository
2. Create a branch: `git checkout -b docs/your-improvement`
3. Make your changes
4. Submit a pull request with a clear description

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## Documentation Updates

This documentation is kept up-to-date with each release. For changes in specific versions, see [CHANGELOG.md](../CHANGELOG.md).

---

Last Updated: November 2024

**AutoDataSetBuilder** - Created by **Raja Muhammad Awais**
