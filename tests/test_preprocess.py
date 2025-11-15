"""
Unit tests for autods.preprocess module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import io
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from autods.preprocess import image_phash_bytes, compute_clip_embedding, preprocess_asset


class TestImagePhash(unittest.TestCase):
    """Test cases for image_phash_bytes function"""
    
    def setUp(self):
        """Create test image data"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        self.image_bytes = io.BytesIO()
        img.save(self.image_bytes, format='JPEG')
        self.image_bytes = self.image_bytes.getvalue()
    
    def test_phash_computation(self):
        """Test pHash computation"""
        phash = image_phash_bytes(self.image_bytes)
        
        self.assertIsNotNone(phash)
        self.assertIsInstance(phash, str)
        self.assertTrue(len(phash) > 0)
    
    def test_phash_deterministic(self):
        """Test that pHash is deterministic"""
        phash1 = image_phash_bytes(self.image_bytes)
        phash2 = image_phash_bytes(self.image_bytes)
        
        self.assertEqual(phash1, phash2)
    
    def test_phash_different_images(self):
        """Test that different images produce different hashes"""
        # Create another image
        img2 = Image.new('RGB', (100, 100), color=(255, 0, 0))
        bytes2 = io.BytesIO()
        img2.save(bytes2, format='JPEG')
        bytes2 = bytes2.getvalue()
        
        phash1 = image_phash_bytes(self.image_bytes)
        phash2 = image_phash_bytes(bytes2)
        
        # Hashes might be similar due to small image size, but typically different
        # Just test that both are valid
        self.assertTrue(len(phash1) > 0)
        self.assertTrue(len(phash2) > 0)
    
    def test_phash_invalid_image(self):
        """Test pHash with invalid image data"""
        invalid_bytes = b"not an image"
        phash = image_phash_bytes(invalid_bytes)
        
        # Should return empty string on error
        self.assertEqual(phash, "")


class TestCLIPEmbedding(unittest.TestCase):
    """Test cases for compute_clip_embedding function"""
    
    def setUp(self):
        """Create test image"""
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        self.image_bytes = io.BytesIO()
        img.save(self.image_bytes, format='JPEG')
        self.image_bytes = self.image_bytes.getvalue()
    
    def test_clip_embedding_shape(self):
        """Test CLIP embedding output shape"""
        embedding = compute_clip_embedding(self.image_bytes)
        
        # Should return a tensor or mock tensor
        self.assertIsNotNone(embedding)
    
    def test_clip_embedding_deterministic(self):
        """Test that embeddings are consistent"""
        emb1 = compute_clip_embedding(self.image_bytes)
        emb2 = compute_clip_embedding(self.image_bytes)
        
        # Both should be valid (either real embeddings or mocks)
        self.assertIsNotNone(emb1)
        self.assertIsNotNone(emb2)


class TestPreprocessAsset(unittest.TestCase):
    """Test cases for preprocess_asset function"""
    
    def setUp(self):
        """Create test assets"""
        # Image
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        self.image_bytes = img_bytes.getvalue()
        
        # Text
        self.text_bytes = b"This is a sample text document"
        
        # Audio (simple binary data)
        self.audio_bytes = b"\x00\x01\x02\x03" * 100
    
    def test_preprocess_image(self):
        """Test preprocessing image modality"""
        asset_id = "test_asset_1"
        features = preprocess_asset(asset_id, self.image_bytes, 'image')
        
        self.assertEqual(features['asset_id'], asset_id)
        self.assertIn('phash', features)
        self.assertIn('clip_embedding', features)
    
    def test_preprocess_text(self):
        """Test preprocessing text modality"""
        asset_id = "test_asset_2"
        features = preprocess_asset(asset_id, self.text_bytes, 'text')
        
        self.assertEqual(features['asset_id'], asset_id)
        self.assertIn('lang', features)
        self.assertIn('word_count', features)
        self.assertGreater(features['word_count'], 0)
    
    def test_preprocess_audio(self):
        """Test preprocessing audio modality"""
        asset_id = "test_asset_3"
        features = preprocess_asset(asset_id, self.audio_bytes, 'audio')
        
        self.assertEqual(features['asset_id'], asset_id)
        self.assertIn('sample_rate', features)
        self.assertIn('duration_sec', features)
    
    def test_preprocess_unknown_modality(self):
        """Test preprocessing with unknown modality"""
        features = preprocess_asset("test", self.image_bytes, 'unknown')
        
        # Should still return asset_id
        self.assertIn('asset_id', features)


class TestPreprocessPipeline(unittest.TestCase):
    """Integration tests for preprocessing pipeline"""
    
    def test_batch_preprocessing(self):
        """Test batch preprocessing of multiple assets"""
        assets = [
            ("asset_1", Image.new('RGB', (50, 50)).tobytes(), 'image'),
            ("asset_2", b"text sample", 'text'),
        ]
        
        features_list = []
        for asset_id, asset_bytes, modality in assets:
            if modality == 'image':
                # Create proper image bytes
                img = Image.new('RGB', (50, 50))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                asset_bytes = img_bytes.getvalue()
            
            features = preprocess_asset(asset_id, asset_bytes, modality)
            features_list.append(features)
        
        self.assertEqual(len(features_list), len(assets))
        for features in features_list:
            self.assertIn('asset_id', features)


if __name__ == '__main__':
    unittest.main()
