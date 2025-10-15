import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def recommend_from_song(song_name, df, n=10):
    """Recommend top-n similar songs to the selected song."""
    # Use the actual column names from your CSV
    track_column = 'song'  # Your CSV uses 'song' not 'track' or 'name'
    artist_column = 'artist'
    
    print(f"🔍 Using track column: '{track_column}', artist column: '{artist_column}'")
    print(f"🔍 Looking for song: '{song_name}'")
    
    # Check if song exists in dataframe
    if song_name not in df[track_column].values:
        available_songs = df[track_column].unique()[:10]  # Show first 10 available songs
        print(f"❌ Song '{song_name}' not found. Available songs: {available_songs}")
        return pd.DataFrame()

    # Select numeric features only (exclude non-feature columns)
    exclude_cols = ['artist', 'song', 'duration_ms', 'explicit', 'year', 'popularity', 'genre']
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    print(f"🔍 Using feature columns: {feature_cols}")
    
    if not feature_cols:
        # Fallback: use all numeric columns except the obvious non-features
        feature_cols = [col for col in numeric_cols if col not in ['year', 'popularity']]
    
    if not feature_cols:
        raise ValueError("No numeric features found for recommendations")
    
    numeric_df = df[feature_cols].fillna(0)

    # Scale features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(numeric_df)

    # Locate the index of the selected song
    idx = df[df[track_column] == song_name].index[0]
    target_vector = features_scaled[idx].reshape(1, -1)

    # Compute similarity between selected song and all others (vector vs matrix)
    sims = cosine_similarity(target_vector, features_scaled)[0]

    # Get top N similar songs (excluding itself)
    similar_indices = sims.argsort()[::-1][1:n+1]
    
    # Build recommendations - get the original rows with all columns
    recs = df.iloc[similar_indices].copy()
    
    # Add similarity scores to the recommendations
    recs = recs.copy()  # Ensure we're working with a copy
    recs['similarity'] = sims[similar_indices]

    # Add Spotify search links (since we don't have Spotify IDs in your CSV)
    recs['spotify_link'] = recs.apply(
        lambda row: f"https://open.spotify.com/search/{row['artist']}%20{row['song']}".replace(' ', '%20'),
        axis=1
    )

    print(f"✅ Generated {len(recs)} recommendations for '{song_name}'")
    print(f"🔍 Recommendation columns: {list(recs.columns)}")
    return recs


def get_available_songs(df):
    """Get list of available songs for the dropdown."""
    track_column = 'song'
    artist_column = 'artist'
    
    return [f"{row[track_column]} - {row[artist_column]}" for _, row in df.iterrows()]


def get_song_mapping(df):
    """Create mapping between display names and actual song names."""
    track_column = 'song'
    artist_column = 'artist'
    
    return {f"{row[track_column]} - {row[artist_column]}": row[track_column] for _, row in df.iterrows()}