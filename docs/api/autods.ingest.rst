=====================================
autods.ingest - Data Ingestion API
=====================================

The ingest module provides tools for fetching, validating, and storing raw data from various sources.

.. automodule:: autods.ingest
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Overview
========

The `IngestClient` class is the main interface for data ingestion:

.. code-block:: python

    from autods.ingest import IngestClient
    
    client = IngestClient(
        s3_bucket="raw",
        db_url="postgresql://user:pass@localhost/db"
    )
    
    result = client.ingest_url(
        url="https://example.com/image.jpg",
        license="cc0",
        source="example"
    )

Key Features
============

- **URL Fetching**: Download data from HTTP/HTTPS URLs
- **Checksum Verification**: SHA256 checksums for integrity verification
- **S3 Storage**: Upload to S3-compatible storage (MinIO)
- **Metadata Tracking**: PostgreSQL database for asset metadata
- **Deduplication**: Automatic detection of duplicate assets
- **Error Handling**: Graceful handling of download failures

Class Reference
===============

.. autoclass:: autods.ingest.IngestClient
   :members:
   :special-members: __init__
   :show-inheritance:
   :member-order: bysource

Examples
========

Ingest a Single URL
-------------------

.. code-block:: python

    from autods.ingest import IngestClient
    import os
    
    client = IngestClient(
        s3_bucket="raw",
        db_url=os.getenv("DB_URL")
    )
    
    result = client.ingest_url(
        url="https://example.com/photo.jpg",
        license="cc0",
        source="my_dataset"
    )
    
    print(f"Asset ID: {result['id']}")
    print(f"S3 Key: {result['s3_key']}")
    print(f"Checksum: {result['checksum']}")
    
    client.close()

Ingest Multiple URLs
--------------------

.. code-block:: python

    urls = [
        "https://example.com/img1.jpg",
        "https://example.com/img2.jpg",
        "https://example.com/img3.jpg",
    ]
    
    client = IngestClient(s3_bucket="raw", db_url=db_url)
    
    ingested = []
    for url in urls:
        try:
            result = client.ingest_url(url, license="cc0", source="batch_import")
            ingested.append(result)
        except Exception as e:
            print(f"Failed to ingest {url}: {e}")
    
    print(f"Successfully ingested {len(ingested)} assets")
    client.close()

See Also
========

- :mod:`autods.preprocess` - Feature extraction and preprocessing
- :mod:`autods.labeling` - Programmatic labeling
- :mod:`autods.shard` - WebDataset shard creation
