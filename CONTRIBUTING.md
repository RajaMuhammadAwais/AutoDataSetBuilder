# Contributing to AutoDataSetBuilder

Thank you for your interest in contributing to AutoDataSetBuilder! We welcome contributions from the community. This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions. Any harassment or discrimination will not be tolerated.

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AutoDataSetBuilder.git
   cd AutoDataSetBuilder
   ```

3. **Add upstream remote** to sync with the main repository:
   ```bash
   git remote add upstream https://github.com/rajamuhammadawais1/AutoDataSetBuilder.git
   ```

4. **Create a new branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Prerequisites

- Python 3.10+
- Poetry (recommended)
- Docker & Docker Compose (for running services)
- Git

### Installing Dependencies

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install project dependencies**:
   ```bash
   poetry install --with dev
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Starting Services

Start the development infrastructure:

```bash
docker-compose up -d
```

This starts:
- MinIO (S3-compatible storage) on port 9000
- PostgreSQL (metadata database) on port 5432
- Label Studio (labeling tool) on port 8080

Verify services are running:
```bash
docker-compose ps
```

---

## Making Changes

### Branch Naming Convention

Use descriptive branch names:
- `feature/add-new-processor` - for new features
- `fix/correct-indexing-bug` - for bug fixes
- `docs/update-readme` - for documentation
- `refactor/simplify-api` - for refactoring
- `test/add-integration-tests` - for tests

### Code Organization

The project structure:
```
AutoDataSetBuilder/
├── sdk/autods/          # Core SDK modules
├── services/            # Microservices
├── tests/               # Test suite
├── docs/                # Documentation
└── examples/            # Example scripts
```

### Creating New Features

1. **Create a new module** in the appropriate location
2. **Add unit tests** in the `tests/` directory
3. **Add documentation** to module docstrings
4. **Update README** if the feature affects API

Example structure for a new feature:

```python
# sdk/autods/new_feature.py
"""
New feature module.

This module provides functionality for X.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class NewFeature:
    """Implementation of new feature."""

    def __init__(self, config: Optional[dict] = None):
        """Initialize feature."""
        self.config = config or {}

    def process(self, data: List[str]) -> List[dict]:
        """Process data.
        
        Args:
            data: Input data list
            
        Returns:
            Processed results
        """
        results = []
        for item in data:
            result = self._process_item(item)
            results.append(result)
        return results

    def _process_item(self, item: str) -> dict:
        """Process single item."""
        logger.info(f"Processing: {item}")
        return {"input": item, "processed": True}


# Example usage
if __name__ == "__main__":
    feature = NewFeature()
    results = feature.process(["a", "b", "c"])
    print(results)
```

---

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_ingest.py

# Run with coverage
poetry run pytest --cov=sdk --cov=services

# Run with verbose output
poetry run pytest -v

# Run specific test
poetry run pytest tests/test_ingest.py::test_ingest_client
```

### Writing Tests

Follow these guidelines:

1. **Test file naming**: `test_<module_name>.py`
2. **Test class naming**: `Test<ClassName>`
3. **Test method naming**: `test_<method_name>_<scenario>`

Example test:

```python
# tests/test_ingest.py
import pytest
from sdk.autods.ingest import IngestClient


class TestIngestClient:
    """Tests for IngestClient."""

    @pytest.fixture
    def client(self):
        """Fixture for IngestClient."""
        return IngestClient(
            s3_bucket="test-bucket",
            db_url="sqlite:///:memory:"
        )

    def test_ingest_url_valid(self, client):
        """Test ingesting a valid URL."""
        # Arrange
        url = "https://example.com/image.jpg"
        license = "cc0"
        source = "test"

        # Act
        result = client.ingest_url(url=url, license=license, source=source)

        # Assert
        assert result is not None
        assert "id" in result
        assert "s3_key" in result

    def test_ingest_url_invalid(self, client):
        """Test ingesting an invalid URL."""
        # Should raise an exception
        with pytest.raises(ValueError):
            client.ingest_url(
                url="not-a-valid-url",
                license="cc0",
                source="test"
            )

    def test_ingest_batch(self, client):
        """Test batch ingestion."""
        urls = ["https://example.com/1.jpg", "https://example.com/2.jpg"]
        results = client.ingest_batch(urls=urls, license="cc0", source="test")
        assert len(results) == 2
```

### Test Coverage

Aim for at least 80% code coverage:

```bash
poetry run pytest --cov=sdk --cov=services --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages following the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or changes
- `chore`: Build process, dependencies, etc.

**Examples:**
```
feat(ingest): add support for AWS S3 URLs
fix(preprocess): correct pHash computation for large images
docs(readme): add installation instructions
test(labeling): add tests for weak label aggregation
```

### Pushing Changes

```bash
# Commit your changes
git add .
git commit -m "feat(module): description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

### Creating a Pull Request

1. Push your branch to your fork
2. Go to the original repository on GitHub
3. Click "Compare & pull request"
4. Fill in the PR template with:
   - **Title**: Clear, descriptive title
   - **Description**: Explain the changes and motivation
   - **Related issues**: Link to any related issues
   - **Testing**: Describe testing performed

5. Submit the PR

**PR Template:**

```markdown
## Description
Brief description of changes

## Motivation
Why are these changes needed?

## Changes
- Change 1
- Change 2
- Change 3

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

### PR Review Process

1. **Automated checks**: CI/CD pipeline runs automatically
2. **Code review**: Maintainers review and provide feedback
3. **Addressing feedback**: Make requested changes
4. **Approval**: Once approved, PR can be merged

---

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these tools:

**Black** (code formatting):
```bash
poetry run black sdk/ services/ tests/
```

**isort** (import sorting):
```bash
poetry run isort sdk/ services/ tests/
```

**Flake8** (linting):
```bash
poetry run flake8 sdk/ services/ tests/
```

**MyPy** (type checking):
```bash
poetry run mypy sdk/ services/
```

### Code Standards

1. **Type hints**: Use type hints for all function signatures
   ```python
   def process_asset(asset_id: str, data: bytes) -> dict:
       pass
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def ingest_url(url: str, license: str) -> dict:
       """Ingest data from a URL.
       
       Args:
           url: The URL to ingest from
           license: License type (e.g., 'cc0', 'apache2')
           
       Returns:
           Dictionary with ingestion result containing 'id' and 's3_key'
           
       Raises:
           ValueError: If URL is invalid
           ConnectionError: If cannot reach URL
       """
   ```

3. **Logging**: Use logging instead of print statements
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   logger.info(f"Processing asset: {asset_id}")
   logger.warning(f"Duplicate detected: {checksum}")
   logger.error(f"Failed to process: {asset_id}", exc_info=True)
   ```

4. **Error handling**: Handle exceptions properly
   ```python
   try:
       result = process_data(data)
   except ValueError as e:
       logger.error(f"Invalid data: {e}")
       raise
   except Exception as e:
       logger.error(f"Unexpected error: {e}", exc_info=True)
       raise RuntimeError(f"Failed to process data") from e
   ```

---

## Documentation

### Documentation Structure

- **README.md**: Overview and quick start
- **docs/architecture.md**: System design
- **docs/api.md**: API reference
- **docs/deployment.md**: Deployment guide
- **Docstrings**: In-code documentation

### Writing Documentation

1. **Use clear language**: Avoid jargon where possible
2. **Provide examples**: Show how to use features
3. **Include diagrams**: For complex concepts
4. **Keep it updated**: Update docs when code changes

### Building Documentation

```bash
# Install doc tools
pip install sphinx sphinx-rtd-theme

# Build HTML docs
sphinx-build -b html docs/ docs/_build/

# View in browser
open docs/_build/index.html
```

---

## Reporting Issues

### Bug Reports

Create a detailed bug report with:

1. **Title**: Clear, concise summary
2. **Environment**: Python version, OS, dependencies
3. **Steps to reproduce**: Clear step-by-step instructions
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Logs/error messages**: Include relevant output
7. **Screenshots**: If applicable

**Bug report template:**
```markdown
## Description
Brief description of the bug

## Environment
- Python: 3.10
- OS: Ubuntu 22.04
- AutoDataSetBuilder: 0.1.0

## Steps to Reproduce
1. ...
2. ...
3. ...

## Expected Behavior
...

## Actual Behavior
...

## Error Message/Logs
```
[error message here]
```

## Screenshots
[if applicable]
```

### Feature Requests

Create a feature request with:

1. **Title**: Clear feature description
2. **Motivation**: Why is this feature needed?
3. **Proposed solution**: How should it work?
4. **Alternatives**: Are there other approaches?
5. **Additional context**: Any other relevant info

---

## Getting Help

- **Documentation**: Check [docs/](docs/)
- **Examples**: See [examples/](examples/)
- **Issues**: Search [existing issues](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/rajamuhammadawais1/AutoDataSetBuilder/discussions)
- **Email**: support@example.com

---

## License

By contributing to this project, you agree that your contributions will be licensed under its MIT License.

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub Contributors page

Thank you for contributing to AutoDataSetBuilder! 🙏
