"""Explicit recommendation schema; identifiers and popularity are never signals."""
import numpy as np
import pandas as pd

FEATURE_COLS = (
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
)


def get_feature_columns():
    return list(FEATURE_COLS)


def validate_features(df):
    missing = set(FEATURE_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing audio features: {', '.join(sorted(missing))}")
    values = df[list(FEATURE_COLS)].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("Audio features must contain finite numbers with no missing values.")
    return values
