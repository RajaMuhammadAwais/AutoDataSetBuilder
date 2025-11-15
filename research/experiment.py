#!/usr/bin/env python3
"""
Reproducible experiment runner (smoke test) for AutoDataSetBuilder.

This script runs a tiny end-to-end pipeline on a couple of public sample images:
- Ingest (upload to MinIO + record metadata)
- Preprocess (pHash + mock CLIP)
- Label (run Snorkel label model)
- Lightweight shard creation (local tar)

Designed to be deterministic and small so it can run in CI as a smoke experiment.
"""
import os
import sys
import time
import logging
from pathlib import Path
import json

# Ensure local SDK import works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk"))

from autods.ingest import IngestClient
from autods.preprocess import preprocess_asset
from autods.labeling import lf_caption_has_animal, lf_caption_is_short, run_label_model

import boto3
from botocore.client import Config
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('research.experiment')


def wait_for_postgres(db_url: str, timeout: int = 30):
    """Wait for Postgres to be reachable."""
    start = time.time()
    while True:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            logger.info("Postgres reachable")
            return True
        except Exception as e:
            if time.time() - start > timeout:
                logger.error(f"Postgres not reachable after {timeout}s: {e}")
                return False
            logger.info("Waiting for Postgres...")
            time.sleep(2)


def ensure_bucket(s3_client, bucket: str):
    """Create bucket if it does not exist (MinIO/S3)."""
    try:
        s3_client.head_bucket(Bucket=bucket)
        logger.info(f"Bucket '{bucket}' already exists")
    except Exception:
        logger.info(f"Creating bucket '{bucket}'")
        try:
            s3_client.create_bucket(Bucket=bucket)
        except Exception as e:
            # Some S3 endpoints require different create signature; ignore if exists
            logger.warning(f"create_bucket warning: {e}")


def run_smoke():
    # Configuration from env
    DB_URL = os.getenv('DB_URL', 'postgresql://test_user:test_password@localhost:5432/test_db')
    S3_ENDPOINT = os.getenv('S3_ENDPOINT_URL', 'http://localhost:9000')
    S3_USER = os.getenv('MINIO_ROOT_USER', 'minioadmin')
    S3_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin')
    RAW_BUCKET = os.getenv('RAW_BUCKET', 'raw')

    # Verify Postgres
    if not wait_for_postgres(DB_URL, timeout=20):
        raise SystemExit(2)

    # Init S3 client
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_USER,
        aws_secret_access_key=S3_PASSWORD,
        config=Config(signature_version='s3v4')
    )

    ensure_bucket(s3, RAW_BUCKET)

    # Initialize DB schema if necessary
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS assets (
            id UUID PRIMARY KEY,
            source_url TEXT,
            s3_key TEXT UNIQUE,
            checksum TEXT UNIQUE,
            license TEXT,
            source TEXT,
            created_at TIMESTAMP
        );''')
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Ensured DB schema (assets table)")
    except Exception as e:
        logger.error(f"Failed to ensure DB schema: {e}")
        raise

    # Initialize ingest client
    ingest_client = IngestClient(s3_bucket=RAW_BUCKET, db_url=DB_URL)

    # Sample public domain images (small)
    samples = [
        {
            'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Dog_in_a_field.jpg/320px-Dog_in_a_field.jpg',
            'caption': 'A brown dog running in a field',
            'license': 'cc0',
            'source': 'wikipedia'
        },
        {
            'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/640px-Cat03.jpg',
            'caption': 'A gray cat',
            'license': 'cc0',
            'source': 'wikipedia'
        }
    ]

    ingested = []
    for s in samples:
        logger.info(f"Ingesting {s['url']}")
        res = ingest_client.ingest_url(url=s['url'], license=s['license'], source=s['source'])
        if res is None:
            logger.error(f"Ingest failed for {s['url']}")
            continue
        res['caption'] = s['caption']
        ingested.append(res)

    if not ingested:
        logger.error("No assets ingested, aborting")
        raise SystemExit(3)

    # Preprocess each ingested asset
    processed = []
    for a in ingested:
        logger.info(f"Fetching {a['s3_key']} from S3")
        obj = s3.get_object(Bucket=RAW_BUCKET, Key=a['s3_key'])
        data = obj['Body'].read()
        features = preprocess_asset(asset_id=a['id'], asset_bytes=data, modality='image')
        features['caption'] = a.get('caption')
        processed.append(features)
        logger.info(f"Processed asset {a['id']} phash={features.get('phash')}")

    # Run labeling
    import pandas as pd

    df = pd.DataFrame(processed)
    lfs = [lf_caption_has_animal, lf_caption_is_short]
    df_labeled = run_label_model(df, lfs)

    logger.info("Labeling results:")
    logger.info(df_labeled[['asset_id', 'caption', 'prob_pos']].to_json(orient='records'))

    # Create a tiny shard (local) as a smoke
    out_dir = Path.cwd() / 'research_output'
    out_dir.mkdir(exist_ok=True)
    index = []
    for i, row in df_labeled.iterrows():
        index.append({'asset_id': row['asset_id'], 'prob_pos': float(row['prob_pos'])})

    index_path = out_dir / 'index.json'
    index_path.write_text(json.dumps(index, indent=2))
    logger.info(f"Wrote index to {index_path}")

    ingest_client.close()

    logger.info("Smoke experiment completed successfully")
    return 0


if __name__ == '__main__':
    rc = run_smoke()
    sys.exit(rc)
