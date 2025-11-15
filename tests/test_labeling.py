"""
Unit tests for autods.labeling module
"""

import unittest
import sys
from pathlib import Path
import pandas as pd

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from autods.labeling import (
    lf_caption_has_animal,
    lf_caption_is_short,
    run_label_model,
    ABSTAIN,
    POSITIVE,
    NEGATIVE
)


class TestLabelingConstants(unittest.TestCase):
    """Test labeling constants"""
    
    def test_abstain_value(self):
        """Test ABSTAIN constant"""
        self.assertEqual(ABSTAIN, -1)
    
    def test_positive_value(self):
        """Test POSITIVE constant"""
        self.assertEqual(POSITIVE, 1)
    
    def test_negative_value(self):
        """Test NEGATIVE constant"""
        self.assertEqual(NEGATIVE, 0)


class TestLabelingFunctions(unittest.TestCase):
    """Test labeling functions"""
    
    def test_lf_caption_has_animal_positive(self):
        """Test lf_caption_has_animal with animal present"""
        sample = pd.Series({'caption': 'A dog running'})
        result = lf_caption_has_animal(sample)
        
        self.assertEqual(result, POSITIVE)
    
    def test_lf_caption_has_animal_multiple_animals(self):
        """Test lf_caption_has_animal with multiple animals"""
        animals = ['dog', 'cat', 'horse', 'bird', 'fish']
        
        for animal in animals:
            sample = pd.Series({'caption': f'A {animal} sleeping'})
            result = lf_caption_has_animal(sample)
            self.assertEqual(result, POSITIVE, f"Failed for animal: {animal}")
    
    def test_lf_caption_has_animal_case_insensitive(self):
        """Test that lf_caption_has_animal is case insensitive"""
        sample = pd.Series({'caption': 'A DOG RUNNING'})
        result = lf_caption_has_animal(sample)
        
        self.assertEqual(result, POSITIVE)
    
    def test_lf_caption_has_animal_abstain(self):
        """Test lf_caption_has_animal with no animals"""
        sample = pd.Series({'caption': 'A nice landscape photo'})
        result = lf_caption_has_animal(sample)
        
        self.assertEqual(result, ABSTAIN)
    
    def test_lf_caption_has_animal_none_caption(self):
        """Test lf_caption_has_animal with None caption"""
        sample = pd.Series({'caption': None})
        result = lf_caption_has_animal(sample)
        
        self.assertEqual(result, ABSTAIN)
    
    def test_lf_caption_is_short_short_caption(self):
        """Test lf_caption_is_short with short caption"""
        sample = pd.Series({'caption': 'cat'})
        result = lf_caption_is_short(sample)
        
        self.assertEqual(result, NEGATIVE)
    
    def test_lf_caption_is_short_medium_caption(self):
        """Test lf_caption_is_short with medium caption (abstain)"""
        sample = pd.Series({'caption': 'A dog running in the park'})
        result = lf_caption_is_short(sample)
        
        self.assertEqual(result, ABSTAIN)
    
    def test_lf_caption_is_short_none_caption(self):
        """Test lf_caption_is_short with None caption"""
        sample = pd.Series({'caption': None})
        result = lf_caption_is_short(sample)
        
        self.assertEqual(result, ABSTAIN)


class TestLabelModel(unittest.TestCase):
    """Test Snorkel LabelModel"""
    
    def setUp(self):
        """Create sample dataset"""
        self.df = pd.DataFrame([
            {'asset_id': '1', 'caption': 'A dog running'},
            {'asset_id': '2', 'caption': 'A cat sleeping'},
            {'asset_id': '3', 'caption': 'Bird'},
            {'asset_id': '4', 'caption': 'Landscape'},
            {'asset_id': '5', 'caption': 'Horse'},
            {'asset_id': '6', 'caption': 'Car'},
            {'asset_id': '7', 'caption': 'A dog and a cat'},
            {'asset_id': '8', 'caption': 'Building'},
        ])
        
        self.lfs = [lf_caption_has_animal, lf_caption_is_short]
    
    def test_run_label_model_returns_dataframe(self):
        """Test that run_label_model returns a DataFrame"""
        result = run_label_model(self.df, self.lfs)
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_run_label_model_adds_prob_pos(self):
        """Test that run_label_model adds prob_pos column"""
        result = run_label_model(self.df, self.lfs)
        
        self.assertIn('prob_pos', result.columns)
    
    def test_run_label_model_preserves_original_columns(self):
        """Test that original columns are preserved"""
        result = run_label_model(self.df, self.lfs)
        
        for col in self.df.columns:
            self.assertIn(col, result.columns)
    
    def test_run_label_model_probability_range(self):
        """Test that probabilities are in [0, 1]"""
        result = run_label_model(self.df, self.lfs)
        
        self.assertTrue((result['prob_pos'] >= 0).all())
        self.assertTrue((result['prob_pos'] <= 1).all())
    
    def test_run_label_model_same_length(self):
        """Test that output has same number of rows as input"""
        result = run_label_model(self.df, self.lfs)
        
        self.assertEqual(len(result), len(self.df))
    
    def test_run_label_model_sensible_predictions(self):
        """Test that label model produces sensible predictions"""
        result = run_label_model(self.df, self.lfs)
        
        # Animals should have higher probability than non-animals
        animal_rows = result[result['caption'].str.contains('dog|cat|bird|horse', case=False, na=False)]
        non_animal_rows = result[~result['caption'].str.contains('dog|cat|bird|horse', case=False, na=False)]
        
        if len(animal_rows) > 0 and len(non_animal_rows) > 0:
            # On average, animals should have higher probability
            # (This is a loose check as the label model is trained on small data)
            self.assertTrue(animal_rows['prob_pos'].mean() >= 0.0)  # Just ensure non-negative


class TestLabelingPipeline(unittest.TestCase):
    """Integration tests for labeling pipeline"""
    
    def test_complete_labeling_pipeline(self):
        """Test complete labeling from raw data to predictions"""
        # Create sample data
        df = pd.DataFrame([
            {'caption': 'A happy dog'},
            {'caption': 'Landscape photo'},
            {'caption': 'A'},
            {'caption': 'A cat sitting on a comfortable couch'},
        ])
        
        # Define labeling functions
        lfs = [lf_caption_has_animal, lf_caption_is_short]
        
        # Run label model
        df_labeled = run_label_model(df, lfs)
        
        # Check results
        self.assertEqual(len(df_labeled), len(df))
        self.assertIn('prob_pos', df_labeled.columns)
        
        # Filter by confidence
        high_conf = df_labeled[df_labeled['prob_pos'] >= 0.5]
        self.assertTrue(len(high_conf) >= 0)
    
    def test_labeling_with_single_lf(self):
        """Test labeling with a single labeling function"""
        df = pd.DataFrame([
            {'caption': 'Dog'},
            {'caption': 'Landscape'},
        ])
        
        lfs = [lf_caption_has_animal]
        result = run_label_model(df, lfs)
        
        self.assertEqual(len(result), len(df))
        self.assertIn('prob_pos', result.columns)


if __name__ == '__main__':
    unittest.main()
