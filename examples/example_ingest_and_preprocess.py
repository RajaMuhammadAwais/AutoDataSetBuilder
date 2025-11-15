#!/usr/bin/env python3
"""
Example: Ingesting and Preprocessing Data with the AutoDataSetBuilder SDK

This example demonstrates how to:
1. Initialize an IngestClient to fetch and store raw data
2. Retrieve data from S3 and preprocess it
3. Extract features (pHash, embeddings) from images

Prerequisites:
- Docker Compose services running (MinIO, PostgreSQL)
- Environment variables set (see config below)
"""

import os
import sys
import logging
from pathlib import Path

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from autods.ingest import IngestClient
from autods.preprocess import preprocess_asset
import boto3
from botocore.client import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def configure_s3_client():
    """Initialize and return an S3 client configured for MinIO."""
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL', 'http://localhost:9000'),
        aws_access_key_id=os.getenv('MINIO_ROOT_USER', 'minioadmin'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin'),
        config=Config(signature_version='s3v4')
    )


def main():
    """Main example flow."""
    
    logger.info("=" * 80)
    logger.info("AutoDataSetBuilder Example: Ingest & Preprocess")
    logger.info("=" * 80)
    
    # Configuration
    db_url = os.getenv(
        'DB_URL',
        'postgresql://autods_user:autods_password@localhost:5432/autods_db'
    )
    raw_bucket = os.getenv('RAW_BUCKET', 'raw')
    processed_bucket = os.getenv('PROCESSED_BUCKET', 'processed')
    
    # Sample image URLs (using public domain images)
    sample_urls = [
        {
            'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Dog_in_a_field.jpg/640px-Dog_in_a_field.jpg',
            'caption': 'A brown dog running in a green field',
            'license': 'cc0',
            'source': 'wikipedia'
        },
        {
            'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg',
            'caption': 'A gray cat looking at the camera',
            'license': 'cc0',
            'source': 'wikipedia'
        },
    ]
    
    # Step 1: Initialize clients
    logger.info("\nStep 1: Initializing clients...")
    try:
        ingest_client = IngestClient(
            s3_bucket=raw_bucket,
            db_url=db_url
        )
        s3_client = configure_s3_client()
        logger.info("✓ Clients initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize clients: {e}")
        return
    
    # Step 2: Ingest sample URLs
    logger.info("\nStep 2: Ingesting sample images...")
    ingested_assets = []
    
    for sample in sample_urls:
        try:
            logger.info(f"  Ingesting: {sample['url']}")
            result = ingest_client.ingest_url(
                url=sample['url'],
                license=sample['license'],
                source=sample['source']
            )
            
            if result:
                ingested_assets.append({
                    **result,
                    'caption': sample['caption'],
                    'modality': 'image'
                })
                logger.info(f"  ✓ Ingested with ID: {result['id']}")
            else:
                logger.warning(f"  ✗ Failed to ingest: {sample['url']}")
        except Exception as e:
            logger.error(f"  ✗ Error ingesting {sample['url']}: {e}")
    
    logger.info(f"✓ Ingested {len(ingested_assets)} assets")
    
    # Step 3: Preprocess assets
    logger.info("\nStep 3: Preprocessing ingested assets...")
    processed_assets = []
    
    for asset in ingested_assets:
        try:
            logger.info(f"  Processing asset: {asset['id']}")
            
            # Retrieve asset from S3
            obj = s3_client.get_object(Bucket=raw_bucket, Key=asset['s3_key'])
            asset_bytes = obj['Body'].read()
            
            # Extract features
            features = preprocess_asset(
                asset_id=asset['id'],
                asset_bytes=asset_bytes,
                modality=asset['modality']
            )
            
            # Add metadata
            features['caption'] = asset['caption']
            features['source'] = asset['s3_key']
            
            processed_assets.append(features)
            logger.info(f"  ✓ Extracted features: phash={features.get('phash', 'N/A')[:16]}...")
            
            # Log feature summary
            if 'clip_embedding' in features:
                embedding_size = len(features['clip_embedding'])
                logger.info(f"    CLIP embedding: {embedding_size}-dimensional vector")
            
        except Exception as e:
            logger.error(f"  ✗ Error processing asset {asset['id']}: {e}")
    
    logger.info(f"✓ Processed {len(processed_assets)} assets")
    
    # Step 4: Display summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    
    logger.info(f"\nIngested Assets: {len(ingested_assets)}")
    for i, asset in enumerate(ingested_assets, 1):
        logger.info(f"  {i}. ID: {asset['id']}")
        logger.info(f"     S3 Key: {asset['s3_key']}")
        logger.info(f"     Checksum: {asset['checksum'][:16]}...")
    
    logger.info(f"\nProcessed Assets: {len(processed_assets)}")
    for i, asset in enumerate(processed_assets, 1):
        logger.info(f"  {i}. ID: {asset['asset_id']}")
        logger.info(f"     Caption: {asset.get('caption', 'N/A')}")
        logger.info(f"     pHash: {asset.get('phash', 'N/A')[:16]}...")
    
    # Step 5: Next steps
    logger.info("\n" + "=" * 80)
    logger.info("Next Steps")
    logger.info("=" * 80)
    logger.info("""
1. Run labeling: See example_labeling.py
2. Run sharding: See example_sharding.py
3. Use Airflow: See example_airflow_dag.py
4. View in Label Studio: http://localhost:8080
    """)
    
    # Cleanup
    logger.info("\nCleaning up...")
    ingest_client.close()
    logger.info("✓ Example completed successfully!")


if __name__ == '__main__':
    main()
