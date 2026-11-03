"""Deterministic, row-identified, scaled cosine recommendations."""
from urllib.parse import quote

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from Recommender.features import validate_features


def recommend_from_song(row_id, df, n=10):
    """Select by unique row_id, excluding that exact row before ranking."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer.")
    if df.empty:
        return pd.DataFrame()
    values = validate_features(df)
    if "row_id" not in df or df.row_id.duplicated().any():
        raise ValueError("Tracks require unique row_id values; use load_songs_from_csv.")
    matches = np.flatnonzero(df.row_id.to_numpy() == row_id)
    if len(matches) != 1:
        raise ValueError("Selected row_id does not exist.")
    position = int(matches[0])
    scaled = StandardScaler().fit_transform(values)
    scores = cosine_similarity(scaled[position:position + 1], scaled)[0]
    candidates = [i for i in range(len(df)) if i != position]
    # Original CSV order breaks ties, including zero/identical feature vectors.
    ranked = sorted(candidates, key=lambda i: (-scores[i], i))[:n]
    result = df.iloc[ranked].copy()
    result["similarity"] = scores[ranked]
    result["spotify_link"] = [
        "https://open.spotify.com/search/" + quote(f"{row.artist} {row.song}", safe="")
        for row in result.itertuples()
    ]
    return result


def get_song_mapping(df):
    return {f"{row.song} - {row.artist} [#{row.row_id}]": row.row_id for row in df.itertuples()}


def get_available_songs(df):
    return list(get_song_mapping(df))
