==========================================
autods.labeling - Programmatic Labeling API
==========================================

The labeling module provides tools for weak supervision using Snorkel labeling functions and label models.

.. automodule:: autods.labeling
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Overview
========

The labeling module implements weak supervision patterns:

- **Labeling Functions**: Domain-specific heuristics for weak labels
- **Label Model**: Probabilistic aggregation of multiple labeling functions
- **Snorkel Integration**: Built on the Snorkel weak supervision framework
- **Probabilistic Labels**: Confidence scores for each prediction

Key Features
============

- **Multiple Labeling Functions**: Combine independent heuristics
- **Label Aggregation**: Snorkel LabelModel learns label function accuracies
- **Abstention**: Labeling functions can abstain when uncertain
- **Probabilistic Output**: Confidence scores (0-1) for each label
- **Scalable**: Processes large datasets efficiently

Constants
=========

.. autodata:: autods.labeling.ABSTAIN
   :annotation: = -1

   Used by labeling functions to indicate they cannot make a decision.

.. autodata:: autods.labeling.POSITIVE
   :annotation: = 1

   Label indicating a positive class.

.. autodata:: autods.labeling.NEGATIVE
   :annotation: = 0

   Label indicating a negative class.

Function Reference
===================

.. autofunction:: autods.labeling.lf_caption_has_animal

.. autofunction:: autods.labeling.lf_caption_is_short

.. autofunction:: autods.labeling.run_label_model

Examples
========

Create Custom Labeling Function
--------------------------------

.. code-block:: python

    from snorkel.labeling import labeling_function
    from autods.labeling import ABSTAIN, POSITIVE, NEGATIVE
    
    @labeling_function()
    def lf_has_dog(x):
        """Labels positive if 'dog' appears in caption."""
        caption = (x.get('caption') or '').lower()
        if 'dog' in caption:
            return POSITIVE
        return ABSTAIN
    
    @labeling_function()
    def lf_long_caption(x):
        """Labels positive if caption has many words."""
        caption = (x.get('caption') or '')
        if len(caption.split()) > 10:
            return POSITIVE
        elif len(caption.split()) < 3:
            return NEGATIVE
        return ABSTAIN

Apply Labeling Functions
------------------------

.. code-block:: python

    import pandas as pd
    from autods.labeling import run_label_model, lf_caption_has_animal
    
    # Create a dataset
    data = [
        {'asset_id': '1', 'caption': 'A dog running'},
        {'asset_id': '2', 'caption': 'A cat sleeping'},
        {'asset_id': '3', 'caption': 'Landscape photo'},
    ]
    df = pd.DataFrame(data)
    
    # Define labeling functions
    lfs = [lf_caption_has_animal]
    
    # Run label model
    df_labeled = run_label_model(df, lfs)
    
    # View results
    print(df_labeled[['asset_id', 'caption', 'prob_pos']])

Filter by Confidence
--------------------

.. code-block:: python

    from autods.labeling import run_label_model
    
    df_labeled = run_label_model(df, lfs)
    
    # Get high-confidence positive predictions
    high_conf = df_labeled[df_labeled['prob_pos'] >= 0.7]
    print(f"High-confidence positives: {len(high_conf)}")
    
    # Get uncertain predictions
    uncertain = df_labeled[
        (df_labeled['prob_pos'] > 0.3) & 
        (df_labeled['prob_pos'] < 0.7)
    ]
    print(f"Uncertain predictions: {len(uncertain)}")

Complete Pipeline
-----------------

.. code-block:: python

    import pandas as pd
    from autods.labeling import run_label_model, lf_caption_has_animal, lf_caption_is_short
    
    # Load preprocessed data
    df = pd.read_csv('preprocessed_data.csv')
    
    # Define labeling functions
    lfs = [
        lf_caption_has_animal,
        lf_caption_is_short,
    ]
    
    # Run label model
    df_labeled = run_label_model(df, lfs)
    
    # Analyze results
    print(f"Total samples: {len(df_labeled)}")
    print(f"Mean confidence: {df_labeled['prob_pos'].mean():.3f}")
    
    # Save labeled data
    df_labeled.to_csv('labeled_data.csv', index=False)

Understanding Label Model
--------------------------

The Snorkel LabelModel:

1. Observes outputs from multiple labeling functions
2. Learns their accuracies automatically (without ground truth)
3. Generates probabilistic labels: P(Y=positive | L)
4. Handles label function dependencies

.. code-block:: python

    # The LabelModel learns:
    # - Accuracy of each labeling function
    # - Correlation between labeling functions
    # - Prior class probabilities
    
    # Output: P(label=1 | labeling function outputs)
    # Values range from 0 (confident negative) to 1 (confident positive)

See Also
========

- :mod:`autods.ingest` - Data ingestion
- :mod:`autods.preprocess` - Feature extraction
- :mod:`autods.shard` - WebDataset shard creation
- `Snorkel Documentation <https://snorkel.org/>`_
