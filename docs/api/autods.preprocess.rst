=========================================
autods.preprocess - Feature Extraction API
=========================================

The preprocess module provides tools for extracting features from raw data.

.. automodule:: autods.preprocess
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Overview
========

The preprocess module includes functions for:

- **Image Perceptual Hashing (pHash)**: Detect near-duplicate images
- **CLIP Embeddings**: Compute multimodal embeddings for images
- **Modality-Specific Processing**: Handle images, text, and audio
- **Feature Aggregation**: Combine multiple preprocessing steps

Key Features
============

- **pHash Generation**: Fast perceptual hashing for near-duplicate detection
- **CLIP Embeddings**: 512-dimensional multimodal vectors
- **Text Processing**: Word count, language detection
- **Audio Processing**: Sample rate, duration estimation
- **Error Resilience**: Graceful handling of corrupted data

Function Reference
===================

.. autofunction:: autods.preprocess.image_phash_bytes

.. autofunction:: autods.preprocess.compute_clip_embedding

.. autofunction:: autods.preprocess.preprocess_asset

Examples
========

Extract Image pHash
-------------------

.. code-block:: python

    from autods.preprocess import image_phash_bytes
    import boto3
    
    s3 = boto3.client('s3', endpoint_url='http://localhost:9000')
    obj = s3.get_object(Bucket='raw', Key='image.jpg')
    image_bytes = obj['Body'].read()
    
    phash = image_phash_bytes(image_bytes)
    print(f"pHash: {phash}")

Compute CLIP Embedding
----------------------

.. code-block:: python

    from autods.preprocess import compute_clip_embedding
    import torch
    
    # Assuming image_bytes contains image data
    embedding = compute_clip_embedding(image_bytes)
    
    if embedding is not None:
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding dimensions: {embedding.flatten().shape[0]}")

Preprocess Asset (Full Pipeline)
--------------------------------

.. code-block:: python

    from autods.preprocess import preprocess_asset
    
    # Get asset bytes from S3
    asset_bytes = ...  # binary image data
    
    # Extract all features
    features = preprocess_asset(
        asset_id='uuid-12345',
        asset_bytes=asset_bytes,
        modality='image'
    )
    
    print(f"Extracted features:")
    print(f"  - pHash: {features['phash']}")
    print(f"  - CLIP embedding dimensions: {len(features['clip_embedding'])}")

Batch Processing
----------------

.. code-block:: python

    from autods.preprocess import preprocess_asset
    from concurrent.futures import ThreadPoolExecutor
    
    assets = [...]  # list of (asset_id, asset_bytes, modality) tuples
    features_list = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(
            lambda a: preprocess_asset(a[0], a[1], a[2]),
            assets
        )
        features_list = list(results)
    
    print(f"Processed {len(features_list)} assets")

See Also
========

- :mod:`autods.ingest` - Data ingestion
- :mod:`autods.labeling` - Programmatic labeling
- :mod:`autods.shard` - WebDataset shard creation
