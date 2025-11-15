'''
Core Labeling Module for the Auto-Dataset Builder Framework.

This module provides:
- Example Snorkel Labeling Functions (LFs).
- A function to run the Snorkel LabelModel for probabilistic label aggregation.
'''

import pandas as pd
import types
import numpy as np

# Provide lightweight stubs for Snorkel components when snorkel is not
# available in the environment (useful for CI and lightweight tests).
try:
    from snorkel.labeling import labeling_function, PandasLFApplier, LabelModel
except Exception:  # pragma: no cover - fallback for test environments
    def labeling_function(*dargs, **dkwargs):
        # Identity decorator: return function unchanged
        def _decorator(func):
            return func
        return _decorator

    class PandasLFApplier:
        def __init__(self, lfs=None):
            self.lfs = lfs or []

        def apply(self, df=None):
            # Apply each LF to the dataframe and return an integer matrix
            n = len(df)
            m = len(self.lfs)
            L = np.full((n, m), -1, dtype=int)
            for j, lf in enumerate(self.lfs):
                for i, row in df.iterrows():
                    try:
                        L[i, j] = int(lf(row))
                    except Exception:
                        L[i, j] = -1
            return L

    class LabelModel:
        def __init__(self, cardinality=2, verbose=False):
            self.cardinality = cardinality

        def fit(self, L_train=None):
            # No-op for stub
            return self

        def predict_proba(self, L=None):
            # Simple heuristic: compute positive ratio per row
            n, m = L.shape
            probs = np.zeros((n, self.cardinality), dtype=float)
            for i in range(n):
                row = L[i]
                pos = (row == 1).sum()
                neg = (row == 0).sum()
                denom = pos + neg
                prob_pos = (pos / denom) if denom > 0 else 0.5
                probs[i, 1] = prob_pos
                probs[i, 0] = 1.0 - prob_pos
            return probs
from typing import List

# Constants
ABSTAIN = -1
POSITIVE = 1
NEGATIVE = 0

# --- Labeling Functions (LFs) ---

@labeling_function()
def lf_caption_has_animal(x: pd.Series) -> int:
    """
    LF that labels an image as POSITIVE if its caption contains common animal words.
    """
    cap = (x.get("caption") or "").lower()
    if any(w in cap for w in ("dog", "cat", "horse", "bird", "fish")):
        return POSITIVE
    return ABSTAIN

@labeling_function()
def lf_caption_is_short(x: pd.Series) -> int:
    """
    LF that labels an image as NEGATIVE if its caption is very short (e.g., less than 5 words).
    """
    cap = (x.get("caption") or "").lower()
    if len(cap.split()) < 5 and len(cap.split()) > 0:
        return NEGATIVE
    return ABSTAIN

# --- Label Model Runner ---

def run_label_model(df: pd.DataFrame, lfs: List) -> pd.DataFrame:
    """
    Applies the LFs to the data and trains/runs the Snorkel LabelModel.

    Args:
        df: A Pandas DataFrame containing the data to be labeled.
        lfs: A list of Snorkel Labeling Functions.

    Returns:
        The input DataFrame with an added 'prob_pos' column containing the
        probabilistic positive label score from the LabelModel.
    """
    print(f"Applying {len(lfs)} labeling functions...")
    applier = PandasLFApplier(lfs=lfs)
    L = applier.apply(df=df)
    
    print("Training LabelModel...")
    # Cardinality is 2 (POSITIVE, NEGATIVE)
    lm = LabelModel(cardinality=2, verbose=True)
    # NOTE: In a real scenario, you would use a training set for lm.fit()
    # Here we fit on the full set for simplicity.
    lm.fit(L_train=L)
    
    print("Predicting probabilistic labels...")
    probs = lm.predict_proba(L)
    
    # The LabelModel outputs probabilities for each class. We take the positive class (index 1).
    df["prob_pos"] = probs[:, POSITIVE]
    
    return df
