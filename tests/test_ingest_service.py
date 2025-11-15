import json
from unittest.mock import patch, MagicMock

import pytest
import json
from unittest.mock import patch, MagicMock

import pytest


from services.ingest_service.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_healthz(client):
    rv = client.get("/healthz")
    assert rv.status_code == 200
    assert rv.data == b"ok"


def test_ingest_success(client):
    fake_result = {"id": "abc", "s3_key": "raw/foo"}

    mock_instance = MagicMock()
    mock_instance.ingest_url.return_value = fake_result
    mock_instance.close.return_value = None

    with patch("sdk.autods.ingest.IngestClient", return_value=mock_instance):
        rv = client.post(
            "/ingest",
            data=json.dumps({"url": "http://example.com/img.jpg", "license": "cc0", "source": "test"}),
            content_type="application/json",
        )

    assert rv.status_code == 200
    body = rv.get_json()
    assert body["result"] == fake_result
    mock_instance.ingest_url.assert_called_once()


def test_ingest_missing_url(client):
    rv = client.post("/ingest", data=json.dumps({}), content_type="application/json")
    assert rv.status_code == 400


def test_ingest_no_ingestclient(client):
    # Simulate import error for IngestClient
    with patch("services.ingest_service.app.IngestClient", side_effect=ImportError("no sdk")):
        rv = client.post(
            "/ingest",
            data=json.dumps({"url": "http://example.com/img.jpg"}),
            content_type="application/json",
        )

    # Should return 503 when backend import fails
    assert rv.status_code == 503
