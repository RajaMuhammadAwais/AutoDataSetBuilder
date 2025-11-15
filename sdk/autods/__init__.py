"""
AutoDataSetBuilder SDK

A modular framework for building, processing, and managing multimodal datasets.

Main Components:
- autods.ingest: Data ingestion from URLs and APIs
- autods.preprocess: Feature extraction and preprocessing
- autods.labeling: Programmatic labeling with Snorkel
- autods.shard: WebDataset shard creation

Example:
    >>> from autods.ingest import IngestClient
    >>> client = IngestClient(s3_bucket="raw", db_url="postgresql://...")
    >>> result = client.ingest_url("https://example.com/image.jpg")
    >>> print(result)
    {'id': 'uuid', 's3_key': 'raw/hash...', 'checksum': 'sha256...'}
"""

from .ingest import IngestClient
from .preprocess import image_phash_bytes, compute_clip_embedding, preprocess_asset
from .labeling import (
    run_label_model,
    lf_caption_has_animal,
    lf_caption_is_short,
    ABSTAIN,
    POSITIVE,
    NEGATIVE
)

__version__ = '0.1.0'
__author__ = 'Raja Muhammad Awais'
__license__ = 'MIT'

__all__ = [
    'IngestClient',
    'image_phash_bytes',
    'compute_clip_embedding',
    'preprocess_asset',
    'run_label_model',
    'lf_caption_has_animal',
    'lf_caption_is_short',
    'ABSTAIN',
    'POSITIVE',
    'NEGATIVE',
]
