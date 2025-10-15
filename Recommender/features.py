
# Recommender/features.py

FEATURE_COLS = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
]

def get_feature_columns():
    """Return list of feature columns used for recommendation."""
    return FEATURE_COLS

