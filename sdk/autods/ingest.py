'''
Core Ingestion Client for the Auto-Dataset Builder Framework.

This module provides the `IngestClient` class, which is responsible for:
- Fetching raw data from a given URL.
- Calculating a checksum for data integrity.
- Uploading the raw data to an S3-compatible object store (e.g., MinIO).
- Recording asset metadata (source URL, S3 key, checksum, license) in a PostgreSQL database.
'''

import os
import time
import uuid
import hashlib
import requests
import boto3
import psycopg2

class IngestClient:
    """A client to handle the ingestion of new data assets."""

    def __init__(self, s3_bucket: str, db_url: str):
        """
        Initializes the IngestClient.

        Args:
            s3_bucket: The name of the S3 bucket for raw data storage.
            db_url: The connection string for the PostgreSQL database.
        """
        # MinIO/S3 connection details
        self.s3_endpoint = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
        self.s3_access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        self.s3_secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
        
        self.s3 = boto3.client(
            "s3", 
            endpoint_url=self.s3_endpoint,
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
            config=boto3.session.Config(signature_version='s3v4')
        )
        self.bucket = s3_bucket
        
        # Database connection
        try:
            self.conn = psycopg2.connect(db_url)
        except psycopg2.OperationalError as e:
            print(f"Error connecting to database: {e}")
            raise

    def ingest_url(self, url: str, license: str = None, source: str = None) -> dict:
        """
        Ingests a file from a URL.

        Downloads the file, calculates its SHA256 checksum, uploads it to the S3
        bucket, and records its metadata in the database.

        Args:
            url: The URL of the file to ingest.
            license: The license of the content (e.g., "cc0", "mit").
            source: The original source of the data (e.g., "common_crawl").

        Returns:
            A dictionary containing the S3 key and checksum of the ingested asset.
        """
        print(f"Ingesting URL: {url}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
            return None

        content = r.content
        checksum = hashlib.sha256(content).hexdigest()
        # Create a unique key using the first 16 chars of the checksum and a timestamp
        key = f"raw/{checksum[:16]}_{int(time.time())}"

        print(f"Uploading to S3 bucket '{self.bucket}' with key '{key}'")
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)

        asset_id = str(uuid.uuid4())
        print(f"Writing metadata to database for asset ID: {asset_id}")
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO assets (id, source_url, s3_key, checksum, license, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (checksum) DO NOTHING;
                """,
                (asset_id, url, key, checksum, license, source)
            )
        self.conn.commit()

        return {"id": asset_id, "s3_key": key, "checksum": checksum}

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
