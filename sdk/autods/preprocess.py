'''
Core Preprocessing Client for the Auto-Dataset Builder Framework.

This module provides functions for modality-specific preprocessing, including:
- Image perceptual hashing (pHash) for near-duplicate detection.
- CLIP embedding computation for multimodal feature extraction.
'''

import io
import torch
import imagehash
from PIL import Image
from typing import Tuple, Optional

# Mock CLIP setup for demonstration. In a real scenario, this would load a model.
try:
    import clip
    # NOTE: We cannot load a real model here as it requires a large download.
    # This is a placeholder for the user's environment.
    CLIP_MODEL, CLIP_PREPROCESS = None, None 
except ImportError:
    CLIP_MODEL, CLIP_PREPROCESS = None, None

def image_phash_bytes(image_bytes: bytes) -> str:
    """
    Computes the perceptual hash (pHash) of an image from its bytes.

    Args:
        image_bytes: The raw bytes of the image file.

    Returns:
        The pHash as a string.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return str(imagehash.phash(img))
    except Exception as e:
        print(f"Error computing pHash: {e}")
        return ""

def compute_clip_embedding(image_bytes: bytes) -> Optional[torch.Tensor]:
    """
    Computes the CLIP image embedding from image bytes.
    NOTE: This function is currently a mock due to environment limitations.

    Args:
        image_bytes: The raw bytes of the image file.

    Returns:
        A torch.Tensor containing the CLIP embedding, or None if the model is not loaded.
    """
    if CLIP_MODEL is None:
        # Mock embedding for demonstration purposes
        return torch.zeros(512) 
        
    try:
        image = CLIP_PREPROCESS(Image.open(io.BytesIO(image_bytes))).unsqueeze(0).to("cpu")
        with torch.no_grad():
            emb = CLIP_MODEL.encode_image(image)
        return emb.cpu()
    except Exception as e:
        print(f"Error computing CLIP embedding: {e}")
        return None

def preprocess_asset(asset_id: str, asset_bytes: bytes, modality: str) -> dict:
    """
    Runs the appropriate preprocessing steps for an asset.

    Args:
        asset_id: The ID of the asset.
        asset_bytes: The raw bytes of the asset.
        modality: The modality of the asset ('image', 'text', 'audio').

    Returns:
        A dictionary of computed features (e.g., 'phash', 'clip_embedding').
    """
    features = {"asset_id": asset_id}
    
    if modality == 'image':
        features['phash'] = image_phash_bytes(asset_bytes)
        clip_emb = compute_clip_embedding(asset_bytes)
        if clip_emb is not None:
            # Convert tensor to a list of floats for easy storage/serialization
            features['clip_embedding'] = clip_emb.flatten().tolist()
            
    elif modality == 'text':
        # Placeholder for text processing (e.g., lang detect, normalization)
        features['lang'] = 'en' # Mock
        features['word_count'] = len(asset_bytes.decode('utf-8', errors='ignore').split())
        
    elif modality == 'audio':
        # Placeholder for audio processing (e.g., resample, VAD)
        features['sample_rate'] = 16000 # Mock
        features['duration_sec'] = 5.0 # Mock
        
    return features
