'''
Service for packaging processed assets into WebDataset TAR shards.

This script reads processed data and writes it into a sharded format suitable
for efficient, large-scale distributed training in PyTorch.
'''

import os
import json
import webdataset as wds
from typing import Iterator, Dict

def create_shards(sample_iter: Iterator[Dict], out_pattern: str, max_count: int = 1000):
    '''
    Creates WebDataset TAR shards from an iterator of samples.

    Args:
        sample_iter: An iterator that yields sample dictionaries.
        out_pattern: The output pattern for the shard files (e.g., "shards/dataset-%06d.tar").
        max_count: The maximum number of samples per shard.
    '''
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(out_pattern), exist_ok=True)

    print(f"Writing shards to {out_pattern} with max {max_count} samples per shard...")
    
    with wds.ShardWriter(out_pattern, maxcount=max_count) as sink:
        for i, sample in enumerate(sample_iter):
            # The sample dictionary must contain the required keys for the sink.
            # The '__key__' is the unique identifier for the sample in the shard.
            # Other keys correspond to the file extensions in the TAR file.
            sink.write({
                "__key__": sample["id"],
                "jpg": sample.get("image_bytes", b''),
                "txt": (sample.get("caption") or "").encode("utf-8"),
                "json": json.dumps(sample.get("meta", {})).encode("utf-8"),
            })
            if (i + 1) % 100 == 0:
                print(f"Wrote {i + 1} samples...")

    print("Finished writing shards.")


# Example Usage (can be run as a script)
if __name__ == '__main__':
    # This is a mock example. In a real pipeline, `sample_iterator` would
    # be populated by querying the database and fetching processed data from S3.
    def get_mock_samples():
        for i in range(2500): # Create 2.5 shards
            yield {
                "id": f"sample_{i:06d}",
                "image_bytes": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82", # 1x1 black pixel PNG
                "caption": f"This is a mock caption for sample {i}.",
                "meta": {"source": "mock", "prob_label": 0.5}
            }

    sample_iterator = get_mock_samples()
    output_pattern = "./shards/mock-dataset-%06d.tar"
    
    create_shards(sample_iterator, output_pattern, max_count=1000)
    
    print(f"Mock shards created. Check the '{os.path.dirname(output_pattern)}' directory.")
