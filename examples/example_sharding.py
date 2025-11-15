#!/usr/bin/env python3
"""
Example: Creating WebDataset Shards for Training

This example demonstrates how to:
1. Create TAR-based WebDataset shards
2. Organize labeled data for efficient training
3. Generate shard indices and metadata

Prerequisites:
- example_ingest_and_preprocess.py and example_labeling.py have been run
- Python dependencies: webdataset, pandas
"""

import sys
import logging
from pathlib import Path
import os
import json
import tarfile
import io
from typing import List, Dict

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShardingService:
    """Simple service for creating WebDataset shards."""
    
    def __init__(self, output_dir: str, shard_size: int = 10):
        """
        Initialize the sharding service.
        
        Args:
            output_dir: Directory to save shards
            shard_size: Number of samples per shard
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.shard_size = shard_size
        self.shard_count = 0
        self.total_samples = 0
    
    def create_shard(self, samples: List[Dict], shard_index: int) -> str:
        """
        Create a TAR shard from samples.
        
        Args:
            samples: List of sample dictionaries
            shard_index: Index for the shard
            
        Returns:
            Path to the created shard file
        """
        shard_name = f"shard-{shard_index:06d}.tar"
        shard_path = self.output_dir / shard_name
        
        logger.info(f"  Creating shard: {shard_name} ({len(samples)} samples)")
        
        with tarfile.open(shard_path, 'w') as tar:
            for i, sample in enumerate(samples):
                # Create sample directory in tar
                sample_dir = f"sample-{i:06d}"
                
                # Add JSON metadata
                metadata_json = json.dumps(sample, indent=2).encode('utf-8')
                metadata_info = tarfile.TarInfo(name=f"{sample_dir}/metadata.json")
                metadata_info.size = len(metadata_json)
                tar.addfile(metadata_info, io.BytesIO(metadata_json))
                
                # Add label if available
                if 'label' in sample:
                    label_data = str(sample['label']).encode('utf-8')
                    label_info = tarfile.TarInfo(name=f"{sample_dir}/label.txt")
                    label_info.size = len(label_data)
                    tar.addfile(label_info, io.BytesIO(label_data))
        
        logger.info(f"  ✓ Created shard: {shard_name} ({shard_path.stat().st_size / 1024:.1f} KB)")
        self.shard_count += 1
        self.total_samples += len(samples)
        
        return str(shard_path)
    
    def create_shards_from_data(self, samples: List[Dict]) -> List[str]:
        """
        Create multiple shards from a list of samples.
        
        Args:
            samples: List of all samples
            
        Returns:
            List of created shard file paths
        """
        shard_paths = []
        
        for i in range(0, len(samples), self.shard_size):
            shard_samples = samples[i:i + self.shard_size]
            shard_index = i // self.shard_size
            shard_path = self.create_shard(shard_samples, shard_index)
            shard_paths.append(shard_path)
        
        return shard_paths
    
    def create_index(self, shard_paths: List[str], metadata: Dict = None):
        """
        Create a shard index file for easy reference.
        
        Args:
            shard_paths: List of shard file paths
            metadata: Additional metadata to include
        """
        index = {
            'shards': [os.path.basename(p) for p in shard_paths],
            'shard_size': self.shard_size,
            'total_shards': len(shard_paths),
            'total_samples': self.total_samples,
            'metadata': metadata or {}
        }
        
        index_path = self.output_dir / 'index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        
        logger.info(f"✓ Created index: {index_path}")
        return index_path


def create_sample_labeled_data() -> List[Dict]:
    """Create sample labeled data for demonstration."""
    return [
        {
            'asset_id': f'sample_{i}',
            'caption': f'Sample image {i}',
            'label': 1 if i % 2 == 0 else 0,
            'confidence': 0.8 + (i % 3) * 0.05
        }
        for i in range(25)
    ]


def main():
    """Main sharding example flow."""
    
    logger.info("=" * 80)
    logger.info("AutoDataSetBuilder Example: Creating WebDataset Shards")
    logger.info("=" * 80)
    
    # Step 1: Prepare data
    logger.info("\nStep 1: Preparing labeled data...")
    samples = create_sample_labeled_data()
    logger.info(f"✓ Prepared {len(samples)} labeled samples")
    
    logger.info("\nSample data:")
    for sample in samples[:3]:
        logger.info(f"  {sample}")
    logger.info(f"  ... and {len(samples) - 3} more")
    
    # Step 2: Create sharding service
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Initializing sharding service...")
    output_dir = Path(__file__).parent / 'output' / 'shards'
    service = ShardingService(
        output_dir=str(output_dir),
        shard_size=10
    )
    logger.info(f"✓ Output directory: {output_dir}")
    
    # Step 3: Create shards
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Creating shards...")
    logger.info("=" * 80)
    
    shard_paths = service.create_shards_from_data(samples)
    logger.info(f"✓ Created {len(shard_paths)} shards")
    
    # Step 4: Create index
    logger.info("\n" + "=" * 80)
    logger.info("Step 4: Creating shard index...")
    service.create_index(
        shard_paths,
        metadata={
            'created_by': 'example_sharding.py',
            'dataset_name': 'sample_dataset',
            'split': 'train'
        }
    )
    
    # Step 5: Display summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    
    logger.info(f"""
Sharding Results:
  Total samples: {service.total_samples}
  Samples per shard: {service.shard_size}
  Total shards created: {service.shard_count}
  Output directory: {output_dir}

Shard Files:
""")
    
    for i, path in enumerate(shard_paths, 1):
        size_kb = Path(path).stat().st_size / 1024
        logger.info(f"  {i}. {Path(path).name} ({size_kb:.1f} KB)")
    
    # Step 6: Show how to load shards
    logger.info("\n" + "=" * 80)
    logger.info("How to Load Shards in Training Code")
    logger.info("=" * 80)
    
    logger.info("""
import webdataset as wds
import json

# Load shards for training
dataset = wds.WebDataset(f'{output_dir}/shard-*.tar')

# Process samples
for sample in dataset:
    metadata = json.loads(sample['metadata.json'])
    label = sample.get('label.txt', '').decode('utf-8')
    
    # Use sample in training...
    print(f"Asset: {metadata['asset_id']}, Label: {label}")
    """)
    
    # Step 7: Next steps
    logger.info("\n" + "=" * 80)
    logger.info("Next Steps")
    logger.info("=" * 80)
    logger.info("""
1. Upload shards to S3: aws s3 sync ./output/shards/ s3://bucket/shards/
2. Load in training pipeline using WebDataset
3. Orchestrate with Airflow: example_airflow_dag.py
4. Monitor with Prometheus/Grafana for production use
    """)
    
    logger.info("✓ Sharding example completed successfully!")


if __name__ == '__main__':
    main()
