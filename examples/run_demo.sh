#!/bin/bash
#
# Minimal end-to-end demo script for the Auto-Dataset Builder Framework.
# This script simulates the core pipeline steps: Ingest -> Preprocess -> Label -> Shard.
#
# PREREQUISITES:
# 1. Docker and docker-compose are installed.
# 2. The services (MinIO, Postgres, Label Studio) are running via `docker-compose up -d`.
# 3. Python dependencies are installed (boto3, psycopg2, requests, webdataset, pandas, snorkel, pillow, imagehash).

set -e # Exit immediately if a command exits with a non-zero status.

PROJECT_DIR=$(dirname "$0")/..
cd "$PROJECT_DIR"

echo "--- 1. Setting up environment and database ---"
# Set environment variables for the SDK to connect to the local services
export S3_ENDPOINT_URL="http://localhost:9000"
export MINIO_ROOT_USER="minioadmin"
export MINIO_ROOT_PASSWORD="minioadmin"
export DB_URL="postgresql://autods_user:autods_password@localhost:5432/autods_db"
export RAW_BUCKET="raw"

# Wait for Postgres to be ready (simplified check)
echo "Waiting for Postgres to be ready..."
sleep 5

# Initialize the database schema (create the 'assets' table)
python3 -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DB_URL'))
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS assets;')
cur.execute('CREATE TABLE assets (id UUID PRIMARY KEY, source_url TEXT, s3_key TEXT, checksum TEXT UNIQUE, license TEXT, source TEXT, created_at TIMESTAMP);')
conn.commit()
conn.close()
print('Database schema initialized.')
"

echo "--- 2. Ingesting a sample image ---"
# We will use a public domain image URL for the demo
SAMPLE_URL="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Dog_in_a_field.jpg/640px-Dog_in_a_field.jpg"
SAMPLE_CAPTION="A brown dog running in a green field under a blue sky."

# Ingest the sample image and get its metadata
INGEST_OUTPUT=$(python3 -c "
import os
from sdk.autods.ingest import IngestClient
client = IngestClient(s3_bucket=os.getenv('RAW_BUCKET'), db_url=os.getenv('DB_URL'))
result = client.ingest_url(url='$SAMPLE_URL', license='cc0', source='wikipedia')
client.close()
print(result)
")

ASSET_ID=$(echo "$INGEST_OUTPUT" | grep -o "'id': '[^']\+'" | cut -d "'" -f 4)
S3_KEY=$(echo "$INGEST_OUTPUT" | grep -o "'s3_key': '[^']\+'" | cut -d "'" -f 4)

if [ -z "$ASSET_ID" ]; then
    echo "Ingestion failed. Exiting."
    exit 1
fi

echo "Ingested Asset ID: $ASSET_ID"
echo "S3 Key: $S3_KEY"

echo "--- 3. Preprocessing and Feature Extraction ---"
# Retrieve the asset from S3 and run preprocessing (pHash, mock CLIP embedding)
PREPROCESS_OUTPUT=$(python3 -c "
import os
import boto3
from sdk.autods.preprocess import preprocess_asset
from botocore.client import Config

# Setup S3 client with MinIO configuration
s3 = boto3.client(
    's3', 
    endpoint_url=os.getenv('S3_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
    aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
    config=Config(signature_version='s3v4')
)

obj = s3.get_object(Bucket=os.getenv('RAW_BUCKET'), Key='$S3_KEY')
asset_bytes = obj['Body'].read()
features = preprocess_asset(asset_id='$ASSET_ID', asset_bytes=asset_bytes, modality='image')
# Add the caption for the labeling step
features['caption'] = '$SAMPLE_CAPTION'
print(features)
")

echo "Preprocessing Output: $PREPROCESS_OUTPUT"

echo "--- 4. Programmatic Labeling (Snorkel) ---"
# Create a mock DataFrame and run the Snorkel LabelModel
LABEL_OUTPUT=$(python3 -c "
import pandas as pd
import json
from sdk.autods.labeling import lf_caption_has_animal, lf_caption_is_short, run_label_model

# Create a DataFrame from the preprocessed data (simplified)
# Note: The output of PREPROCESS_OUTPUT is a string representation of a dict.
# We need to clean it up for json.loads.
import re
output_str = '$PREPROCESS_OUTPUT'
# Simple replacement for single quotes to double quotes for JSON compatibility
output_str = output_str.replace(\"'\", '\"')
# Fix for boolean/None values if they were present (not strictly needed here but good practice)
output_str = re.sub(r'True', 'true', output_str)
output_str = re.sub(r'False', 'false', output_str)
output_str = re.sub(r'None', 'null', output_str)

data = json.loads(output_str)
df = pd.DataFrame([data])
df['caption'] = '$SAMPLE_CAPTION' # Add caption back for LF
df['id'] = '$ASSET_ID'

lfs = [lf_caption_has_animal, lf_caption_is_short]
labeled_df = run_label_model(df, lfs)

# Extract the probabilistic label
prob_pos = labeled_df['prob_pos'].iloc[0]
print(f'Probabilistic Positive Label: {prob_pos:.4f}')
")

echo "$LABEL_OUTPUT"

echo "--- 5. Sharding (WebDataset) ---"
# Create a mock sample iterator and run the sharder
SHARD_OUTPUT=$(python3 -c "
import os
import boto3
import json
from sdk.autods.preprocess import preprocess_asset
from services.sharder.create_shards import create_shards
from botocore.client import Config

# 1. Fetch the raw image bytes again (in a real system, this would be processed data)
s3 = boto3.client(
    's3', 
    endpoint_url=os.getenv('S3_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
    aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
    config=Config(signature_version='s3v4')
)
obj = s3.get_object(Bucket=os.getenv('RAW_BUCKET'), Key='$S3_KEY')
asset_bytes = obj['Body'].read()

# 2. Prepare the sample for sharding
sample = {
    'id': '$ASSET_ID',
    'image_bytes': asset_bytes,
    'caption': '$SAMPLE_CAPTION',
    'meta': {
        'source': 'wikipedia',
        'prob_label': 0.99, # Mock high confidence label
        'phash': 'mock_phash',
        'clip_emb_mock': 'mock_emb'
    }
}

# 3. Run the sharder
create_shards(iter([sample]), './shards/demo-dataset-%06d.tar', max_count=100)

print('Sharding complete. Check ./shards/demo-dataset-000000.tar')
")

echo "$SHARD_OUTPUT"

echo "--- Demo Complete ---"
echo "You can now inspect the generated shard file: ./shards/demo-dataset-000000.tar"
echo "You can also use Label Studio at http://localhost:8080"
echo "MinIO console is at http://localhost:9001"
