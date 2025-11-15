"""
Pytest configuration and fixtures
"""

"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path
import os

# Make repository root importable so tests can `import services` and other
# top-level modules. Insert SDK path as well for direct imports used in tests.
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
SDK_PATH = ROOT / "sdk"
sys.path.insert(0, str(SDK_PATH))

# Set environment variables for testing
os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["MINIO_ROOT_USER"] = "minioadmin"
os.environ["MINIO_ROOT_PASSWORD"] = "minioadmin"
os.environ["DB_URL"] = "postgresql://autods_user:autods_password@localhost:5432/autods_db"


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    test_data = Path(__file__).parent / "data"
    test_data.mkdir(exist_ok=True)
    return test_data


@pytest.fixture
def mock_s3_config():
    """Provide mock S3 configuration"""
    return {
        "endpoint_url": "http://localhost:9000",
        "access_key_id": "minioadmin",
        "secret_access_key": "minioadmin",
        "bucket": "test-bucket",
    }


@pytest.fixture
def mock_db_config():
    """Provide mock database configuration"""
    return {"url": "postgresql://test:test@localhost/test_db"}


def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_services: mark test as requiring Docker services"
    )
