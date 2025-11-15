"""Core Ingestion Client for the Auto-Dataset Builder Framework.

This module provides the :class:`IngestClient` class, which is responsible for:
"""

from __future__ import annotations

import os
import time
import uuid
import hashlib
import types
from typing import Optional, Dict

# Optional external dependencies: provide lightweight stubs when running in
# constrained test environments so unit tests can import the module without
# installing heavy packages (boto3, psycopg2, requests). In production these
# packages should be installed and the real implementations will be used.
try:
    import requests
except Exception:  # pragma: no cover - fallback for CI/test containers
    requests = types.SimpleNamespace()

    def _requests_get(*args, **kwargs):
        raise ImportError("requests is required to perform HTTP downloads")

    requests.get = _requests_get

try:
    import boto3
except Exception:  # pragma: no cover
    boto3 = types.SimpleNamespace()

    def _boto3_client(*args, **kwargs):
        raise ImportError("boto3 is required to access S3/MinIO")

    boto3.client = _boto3_client

try:
    import psycopg2
except Exception:  # pragma: no cover
    psycopg2 = types.SimpleNamespace()

    def _psycopg2_connect(*args, **kwargs):
        raise ImportError("psycopg2 is required for PostgreSQL access")

    psycopg2.connect = _psycopg2_connect


class IngestClient:
    """A client to handle ingestion of new data assets.

    The implementation is intentionally defensive so it can be imported in
    lightweight CI environments. Runtime behaviour will raise clear errors
    when optional dependencies are missing.
    """

    def __init__(self, s3_bucket: str, db_url: str):
        # MinIO/S3 connection details
        self.s3_endpoint = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
        self.s3_access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        self.s3_secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

        # Database connection (establish early so DB errors surface on init)
        try:
            self.conn = psycopg2.connect(db_url)
        except Exception as e:
            # Surface connection problems to callers/tests
            raise

        # Create S3 client; if boto3 is not present the attribute will be None
        try:
            try:
                session_cfg = boto3.session.Config(signature_version="s3v4")
            except Exception:
                session_cfg = None

            if session_cfg is not None:
                self.s3 = boto3.client(
                    "s3",
                    endpoint_url=self.s3_endpoint,
                    aws_access_key_id=self.s3_access_key,
                    aws_secret_access_key=self.s3_secret_key,
                    config=session_cfg,
                )
            else:
                self.s3 = boto3.client(
                    "s3",
                    endpoint_url=self.s3_endpoint,
                    aws_access_key_id=self.s3_access_key,
                    aws_secret_access_key=self.s3_secret_key,
                )
        except Exception:
            self.s3 = None

        self.bucket = s3_bucket

    def close(self) -> None:
        """Close external resources (DB connection and S3 client where applicable)."""
        try:
            if getattr(self, "conn", None):
                try:
                    self.conn.close()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            s3 = getattr(self, "s3", None)
            if s3 is not None:
                close_fn = getattr(s3, "close", None)
                if callable(close_fn):
                    try:
                        close_fn()
                    except Exception:
                        pass
        except Exception:
            pass

    def ingest_url(self, url: str, license: Optional[str] = None, source: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Download a URL, upload to S3, and record metadata in Postgres.

        Returns a dict with `id`, `s3_key`, and `checksum` on success; or
        `None` if the download failed.
        """
        # Attempt to download the URL; network errors or missing `requests`
        # should result in a graceful None return so callers can handle it.
        try:
            r = requests.get(url, timeout=30)
        except Exception:
            return None

        # allow requests stub to raise ImportError in constrained envs
        try:
            r.raise_for_status()
        except Exception:
            return None

        content = r.content
        checksum = hashlib.sha256(content).hexdigest()
        key = f"raw/{checksum[:16]}_{int(time.time())}"

        if self.s3 is None:
            raise RuntimeError("S3 client not available")

        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)

        asset_id = str(uuid.uuid4())
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO assets (id, source_url, s3_key, checksum, license, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (checksum) DO NOTHING;
                """,
                (asset_id, url, key, checksum, license, source),
            )
        self.conn.commit()

        return {"id": asset_id, "s3_key": key, "checksum": checksum}
