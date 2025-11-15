"""
Example: Complete Airflow DAG for AutoDataSetBuilder Pipeline

This DAG demonstrates how to orchestrate the complete dataset building pipeline:
1. Ingest data from URLs
2. Preprocess and extract features
3. Apply programmatic labeling
4. Create training-ready shards
5. Monitor and notify on completion

Prerequisites:
- Airflow is installed and initialized
- Environment variables are configured
- Services (MinIO, PostgreSQL) are running
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments for all tasks
default_args = {
    'owner': 'autods',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['admin@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'auto_dataset_dag',
    default_args=default_args,
    description='End-to-end dataset building pipeline',
    schedule_interval='@daily',  # Run daily
    catchup=False,
)


def setup_environment(**context):
    """Setup environment variables and validate configuration."""
    logger.info("Setting up environment...")
    
    # Validate critical environment variables
    required_vars = [
        'S3_ENDPOINT_URL',
        'MINIO_ROOT_USER',
        'MINIO_ROOT_PASSWORD',
        'DB_URL',
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    logger.info("✓ Environment setup successful")
    context['task_instance'].xcom_push(key='setup_complete', value=True)


def ingest_data(**context):
    """Ingest sample data from URLs."""
    logger.info("Starting data ingestion...")
    
    # In production, this would fetch URLs from a data source
    sample_urls = [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
    ]
    
    logger.info(f"Ingesting {len(sample_urls)} items")
    
    # Push the ingested asset IDs for downstream tasks
    context['task_instance'].xcom_push(key='ingested_assets', value=sample_urls)
    
    logger.info("✓ Data ingestion complete")


def preprocess_data(**context):
    """Preprocess ingested data and extract features."""
    logger.info("Starting preprocessing...")
    
    ingested_assets = context['task_instance'].xcom_pull(
        task_ids='ingest_data',
        key='ingested_assets'
    )
    
    logger.info(f"Preprocessing {len(ingested_assets)} assets")
    logger.info("Extracting features: pHash, CLIP embeddings, deduplication")
    
    # In production, this would run the actual preprocessing
    processed_count = len(ingested_assets)
    context['task_instance'].xcom_push(key='processed_assets', value=processed_count)
    
    logger.info("✓ Preprocessing complete")


def label_data(**context):
    """Apply programmatic labeling with Snorkel."""
    logger.info("Starting programmatic labeling...")
    
    processed_count = context['task_instance'].xcom_pull(
        task_ids='preprocess_data',
        key='processed_assets'
    )
    
    logger.info(f"Labeling {processed_count} processed assets")
    logger.info("Applying Snorkel labeling functions and LabelModel aggregation")
    
    # In production, this would run actual labeling
    labeled_count = processed_count
    high_conf_count = int(labeled_count * 0.75)  # Mock high-confidence samples
    
    context['task_instance'].xcom_push(key='labeled_assets', value=labeled_count)
    context['task_instance'].xcom_push(key='high_confidence', value=high_conf_count)
    
    logger.info(f"✓ Labeling complete: {high_conf_count}/{labeled_count} high-confidence")


def create_shards(**context):
    """Create WebDataset shards from labeled data."""
    logger.info("Starting shard creation...")
    
    labeled_count = context['task_instance'].xcom_pull(
        task_ids='label_data',
        key='labeled_assets'
    )
    
    logger.info(f"Creating shards from {labeled_count} labeled samples")
    logger.info("Shard size: 1000 samples per shard (WebDataset format)")
    
    # In production, this would create actual shards
    shard_count = (labeled_count + 999) // 1000
    context['task_instance'].xcom_push(key='created_shards', value=shard_count)
    
    logger.info(f"✓ Shard creation complete: {shard_count} shards created")


def upload_to_storage(**context):
    """Upload shards to S3 storage."""
    logger.info("Uploading shards to S3...")
    
    shard_count = context['task_instance'].xcom_pull(
        task_ids='create_shards',
        key='created_shards'
    )
    
    logger.info(f"Uploading {shard_count} shards to S3")
    logger.info(f"S3 endpoint: {os.getenv('S3_ENDPOINT_URL')}")
    
    # In production, this would upload to S3
    logger.info("✓ Upload complete")


def generate_report(**context):
    """Generate pipeline execution report."""
    logger.info("Generating pipeline report...")
    
    # Pull data from upstream tasks
    ingested = context['task_instance'].xcom_pull(
        task_ids='ingest_data',
        key='ingested_assets'
    )
    processed = context['task_instance'].xcom_pull(
        task_ids='preprocess_data',
        key='processed_assets'
    )
    labeled = context['task_instance'].xcom_pull(
        task_ids='label_data',
        key='labeled_assets'
    )
    high_conf = context['task_instance'].xcom_pull(
        task_ids='label_data',
        key='high_confidence'
    )
    shards = context['task_instance'].xcom_pull(
        task_ids='create_shards',
        key='created_shards'
    )
    
    report = f"""
    ========================================
    Pipeline Execution Report
    ========================================
    
    Execution Date: {datetime.now().isoformat()}
    
    Pipeline Statistics:
    - Assets Ingested: {len(ingested)}
    - Assets Processed: {processed}
    - Assets Labeled: {labeled}
    - High-Confidence Samples: {high_conf}
    - Shards Created: {shards}
    
    Success Rate: 100%
    
    ========================================
    """
    
    logger.info(report)
    context['task_instance'].xcom_push(key='report', value=report)
    logger.info("✓ Report generated")


# Task definitions
with dag:
    
    # Setup task
    setup = PythonOperator(
        task_id='setup_environment',
        python_callable=setup_environment,
        provide_context=True,
    )
    
    # Main pipeline tasks
    with TaskGroup('pipeline') as pipeline_group:
        
        ingest = PythonOperator(
            task_id='ingest_data',
            python_callable=ingest_data,
            provide_context=True,
        )
        
        preprocess = PythonOperator(
            task_id='preprocess_data',
            python_callable=preprocess_data,
            provide_context=True,
        )
        
        label = PythonOperator(
            task_id='label_data',
            python_callable=label_data,
            provide_context=True,
        )
        
        shard = PythonOperator(
            task_id='create_shards',
            python_callable=create_shards,
            provide_context=True,
        )
        
        upload = PythonOperator(
            task_id='upload_to_storage',
            python_callable=upload_to_storage,
            provide_context=True,
        )
        
        # Task dependencies
        ingest >> preprocess >> label >> shard >> upload
    
    # Post-pipeline tasks
    report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
        provide_context=True,
    )
    
    # Cleanup (optional)
    cleanup = BashOperator(
        task_id='cleanup',
        bash_command='echo "Cleaning up temporary files..."',
    )
    
    # DAG dependencies
    setup >> pipeline_group >> report >> cleanup


if __name__ == '__main__':
    # This allows testing the DAG
    dag.test()
