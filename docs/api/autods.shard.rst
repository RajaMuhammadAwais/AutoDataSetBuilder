========================================
autods.shard - WebDataset Sharding API
========================================

The shard module provides tools for creating and managing WebDataset TAR-based shards.

.. warning::

   This module is currently a placeholder. Sharding functionality will be implemented to create
   WebDataset-compatible TAR archives for efficient training.

Overview
========

The shard module will provide:

- **TAR Shard Creation**: Create WebDataset-compatible TAR archives
- **Indexing**: Generate indices for efficient shard discovery
- **Distribution**: Split data across multiple shards for parallel loading
- **Metadata Management**: Store shard metadata and statistics

Planned Features
================

- **ShardingService**: Main class for shard creation
- **TAR Encoding**: Efficient encoding of samples into TAR format
- **Index Generation**: Create JSON indices for shard metadata
- **Streaming Support**: Stream-friendly shard creation
- **Cloud Upload**: Direct upload to S3 or other object stores

Example Usage (Planned)
========================

.. code-block:: python

    from autods.shard import ShardingService
    
    # Initialize service
    shard_service = ShardingService(
        output_dir="./shards",
        shard_size=1000,
        compression='gzip'
    )
    
    # Create shards from labeled data
    shard_paths = shard_service.create_shards_from_data(
        samples=labeled_samples,
        metadata={'dataset': 'my_dataset', 'split': 'train'}
    )
    
    # Load shards in training code
    import webdataset as wds
    dataset = wds.WebDataset(f"{shard_dir}/shard-*.tar")
    
    for sample in dataset:
        x = sample['image.jpg']
        y = sample['label.txt']
        # Use in training...

Related Modules
===============

- :mod:`autods.ingest` - Data ingestion
- :mod:`autods.preprocess` - Feature extraction
- :mod:`autods.labeling` - Programmatic labeling

External Resources
===================

- `WebDataset Documentation <https://github.com/webdataset/webdataset>`_
- `PyTorch DataLoader with WebDataset <https://pytorch.org/docs/stable/data.html>`_

Implementation Notes
====================

When implemented, the shard module should:

1. Accept labeled samples with metadata
2. Group samples by shard (default 1000 per shard)
3. Create TAR archives with JSON metadata files
4. Generate index file listing all shards
5. Support compression (gzip, xz) for space efficiency
6. Enable streaming to S3 during creation
7. Provide utilities for loading shards in training code
