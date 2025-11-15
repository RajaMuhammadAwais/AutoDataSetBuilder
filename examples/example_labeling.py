#!/usr/bin/env python3
"""
Example: Programmatic Labeling with Snorkel

This example demonstrates how to:
1. Create custom labeling functions
2. Apply labeling functions to data
3. Run the Snorkel LabelModel to aggregate labels probabilistically
4. Display label statistics

Prerequisites:
- example_ingest_and_preprocess.py has been run (data exists)
- Python dependencies: pandas, snorkel
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from autods.labeling import (
    lf_caption_has_animal,
    lf_caption_is_short,
    run_label_model
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_dataset():
    """Create a sample dataset for labeling demonstration."""
    data = [
        {
            'asset_id': '1',
            'caption': 'A dog running in the field',
            'source': 'example'
        },
        {
            'asset_id': '2',
            'caption': 'A cat sitting on the floor',
            'source': 'example'
        },
        {
            'asset_id': '3',
            'caption': 'A bird',
            'source': 'example'
        },
        {
            'asset_id': '4',
            'caption': 'Nice landscape',
            'source': 'example'
        },
        {
            'asset_id': '5',
            'caption': 'Horse running in the meadow',
            'source': 'example'
        },
        {
            'asset_id': '6',
            'caption': 'Car',
            'source': 'example'
        },
        {
            'asset_id': '7',
            'caption': 'A dog and a cat playing together',
            'source': 'example'
        },
        {
            'asset_id': '8',
            'caption': 'Building architecture',
            'source': 'example'
        },
    ]
    return pd.DataFrame(data)


def main():
    """Main labeling example flow."""
    
    logger.info("=" * 80)
    logger.info("AutoDataSetBuilder Example: Programmatic Labeling with Snorkel")
    logger.info("=" * 80)
    
    # Step 1: Load or create dataset
    logger.info("\nStep 1: Loading dataset...")
    df = create_sample_dataset()
    logger.info(f"✓ Loaded {len(df)} samples")
    logger.info(f"\nSample data:")
    logger.info(df.to_string(index=False))
    
    # Step 2: Define labeling functions
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Defining labeling functions...")
    logger.info("=" * 80)
    
    lfs = [
        lf_caption_has_animal,
        lf_caption_is_short,
    ]
    
    logger.info(f"Labeling functions ({len(lfs)}):")
    for lf in lfs:
        logger.info(f"  - {lf.__name__}: {lf.__doc__}")
    
    # Step 3: Apply labeling functions
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Applying labeling functions...")
    logger.info("=" * 80)
    
    try:
        df_labeled = run_label_model(df, lfs)
        logger.info("✓ Labeling completed successfully")
    except Exception as e:
        logger.error(f"✗ Error during labeling: {e}")
        return
    
    # Step 4: Display results
    logger.info("\n" + "=" * 80)
    logger.info("Step 4: Label Model Results")
    logger.info("=" * 80)
    
    # Show detailed results
    result_cols = ['asset_id', 'caption', 'prob_pos']
    logger.info(f"\nDetailed Results ({len(df_labeled)} samples):")
    logger.info(df_labeled[result_cols].to_string(index=False))
    
    # Statistics
    logger.info("\n" + "-" * 80)
    logger.info("Label Statistics:")
    logger.info("-" * 80)
    
    prob_pos = df_labeled['prob_pos']
    logger.info(f"  Mean probability (positive): {prob_pos.mean():.4f}")
    logger.info(f"  Std deviation: {prob_pos.std():.4f}")
    logger.info(f"  Min: {prob_pos.min():.4f}")
    logger.info(f"  Max: {prob_pos.max():.4f}")
    logger.info(f"  Median: {prob_pos.median():.4f}")
    
    # Distribution
    logger.info("\n  Distribution (by confidence ranges):")
    low = (prob_pos < 0.33).sum()
    mid = ((prob_pos >= 0.33) & (prob_pos < 0.67)).sum()
    high = (prob_pos >= 0.67).sum()
    
    logger.info(f"    Low confidence (< 0.33): {low} samples")
    logger.info(f"    Mid confidence (0.33-0.67): {mid} samples")
    logger.info(f"    High confidence (>= 0.67): {high} samples")
    
    # Step 5: Filter high-confidence samples
    logger.info("\n" + "=" * 80)
    logger.info("Step 5: Filtering High-Confidence Samples (>= 0.7)")
    logger.info("=" * 80)
    
    high_conf = df_labeled[df_labeled['prob_pos'] >= 0.7]
    logger.info(f"\nHigh-Confidence Samples ({len(high_conf)}):")
    logger.info(high_conf[result_cols].to_string(index=False))
    
    # Step 6: Summary and next steps
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    logger.info(f"""
Total samples labeled: {len(df_labeled)}
High-confidence samples: {len(high_conf)}
High-confidence rate: {len(high_conf)/len(df_labeled)*100:.1f}%

Next steps:
1. Review labels in Label Studio: http://localhost:8080
2. Run sharding to prepare for training: example_sharding.py
3. Integrate with Airflow for production: example_airflow_dag.py
    """)
    
    logger.info("✓ Labeling example completed successfully!")


if __name__ == '__main__':
    main()
