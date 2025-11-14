# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features in development

### Changed
- Modifications to existing functionality

### Deprecated
- Features scheduled for removal

### Removed
- Features that were removed

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes

---

## [0.1.0] - 2024-01-01

### Added
- Initial release of AutoDataSetBuilder by Raja Muhammad Awais
- Core SDK with modular components:
  - Ingestion service for data collection
  - Preprocessing service for feature extraction
  - Labeling service with Snorkel weak supervision
  - Sharding service for dataset creation
- Docker Compose stack with MinIO, PostgreSQL, and Label Studio
- Comprehensive documentation
- CI/CD pipelines with GitHub Actions
- Example scripts and demonstrations

### Features
- **Ingestion**: Fetch and validate data from URLs, APIs, and databases
- **Preprocessing**: Extract perceptual hashes and embeddings
- **Labeling**: Weak supervision with programmatic label functions
- **Sharding**: Create WebDataset-compatible TAR archives
- **Infrastructure**: Docker Compose setup for local development
- **Testing**: Unit and integration test suites
- **Documentation**: Architecture guide, API reference, deployment guide

---

## How to Use This Changelog

### For Users
- Check the [Unreleased] section to see what's coming
- Review version sections to see what changed in each release
- Look for [Security] sections to stay informed about fixes

### For Developers
- Add entries to [Unreleased] as you work
- When releasing, create a new version section
- Format changes according to the categories above

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Upcoming removal (still works)
- **Removed**: Now removed (breaks compatibility)
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Example Entry

```markdown
### Added
- Support for parallel preprocessing with GPU acceleration (#42)
- New `extract_clip_embedding()` function in preprocess module
- Configuration option for batch processing size

### Fixed
- Memory leak in S3 file handling (#38)
- Incorrect deduplication for certain file formats (#39)
- Missing error handling for network timeouts (#40)

### Security
- Updated dependencies to patch security vulnerabilities (CVE-2024-1234)
```

---

## Release Process

1. **Create PR** with changelog updates
2. **Tag version** following semantic versioning: `v0.1.0`
3. **GitHub Actions** automatically:
   - Builds and pushes Docker images
   - Publishes to PyPI
   - Creates GitHub Release
   - Deploys to staging environment
4. **Manual approval** for production deployment
5. **Release notes** automatically generated

---

## Versioning

Version format: `MAJOR.MINOR.PATCH[-PRERELEASE]`

Examples:
- `0.1.0` - First release
- `0.2.0` - New features (minor bump)
- `0.2.1` - Bug fix (patch bump)
- `1.0.0` - Major release
- `1.0.0-alpha` - Pre-release
- `1.0.0-beta.1` - Beta version

---

## Links

- [GitHub Repository](https://github.com/rajamuhammadawais1/AutoDataSetBuilder)
- [GitHub Releases](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/releases)
- [PyPI Package](https://pypi.org/project/auto-dataset-builder/)
- [Documentation](docs/)
