import os
import pandas as pd
from pathlib import Path


# ----------------------------------------------------------
# 🧭 Default CSV Path (Corrected)
# ----------------------------------------------------------
# Use the correct path to your CSV file
DEFAULT_CSV_PATH = r"C:\Users\TSHIFHIWA AUSTIN\OneDrive\Desktop\spotify recommender\Recommender\songs_normalize.csv"

# Alternative flexible approach that also works:
def get_default_csv_path():
    """Get the default CSV path - using the correct location."""
    # The CSV is in the same folder as data.py (Recommender folder)
    csv_in_recommender = Path(__file__).parent / "songs_normalize.csv"
    
    # Your specific path
    specific_path = r"C:\Users\TSHIFHIWA AUSTIN\OneDrive\Desktop\spotify recommender\Recommender\songs_normalize.csv"
    
    # Check which path exists
    if Path(specific_path).exists():
        print(f"✅ Found CSV file at: {specific_path}")
        return specific_path
    elif csv_in_recommender.exists():
        print(f"✅ Found CSV file at: {csv_in_recommender}")
        return str(csv_in_recommender)
    else:
        # Show available files for debugging
        recommender_dir = Path(__file__).parent
        available_files = list(recommender_dir.glob("*.csv"))
        if available_files:
            print("📁 Available CSV files in Recommender folder:")
            for file in available_files:
                print(f"   - {file.name}")
        return None

# Use the flexible approach
DEFAULT_CSV_PATH = get_default_csv_path()


# ----------------------------------------------------------
# 🧹 Helper: Validate and Clean the CSV
# ----------------------------------------------------------
def validate_and_clean_csv(csv_path, save_clean_copy=True):
    """
    Validate and clean the songs CSV file.

    Ensures that:
    - File exists and is readable.
    - Required columns exist for recommendations.
    - Duplicates and invalid rows are removed.
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        # Show helpful error message
        error_msg = f"❌ CSV file not found at: {csv_path}\n\n"
        error_msg += "Please check:\n"
        error_msg += "1. The file 'songs_normalize.csv' should be in your Recommender folder\n"
        error_msg += "2. The file name should be exactly 'songs_normalize.csv'\n"
        error_msg += "3. Or update the DEFAULT_CSV_PATH in data.py\n"
        
        # Show what files are available
        if csv_path.parent.exists():
            available_files = list(csv_path.parent.glob("*.csv"))
            if available_files:
                error_msg += "\n📁 Available CSV files in this folder:\n"
                for file in available_files:
                    error_msg += f"   - {file.name}\n"
        
        raise FileNotFoundError(error_msg)

    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")
    except Exception as e:
        raise ValueError(f"❌ Error reading CSV file: {e}")

    # Check for required columns - be more flexible
    required_columns = ['id', 'name', 'artist']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    # Show available columns for debugging
    print(f"🔍 Checking columns - looking for: {required_columns}")
    print(f"📋 Actual columns in CSV: {list(df.columns)}")
    
    if missing_columns:
        print(f"⚠️ CSV missing some expected columns: {missing_columns}")
        # Don't raise error, just warn and continue with available columns

    # Clean and validate IDs if they exist
    if "id" in df.columns:
        df["id"] = df["id"].astype(str).str.strip()
        # Remove rows with empty IDs but don't require strict Spotify ID format
        initial_count = len(df)
        df = df[df["id"].str.len() > 0].copy()
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} rows with empty IDs")

    # Remove duplicates and reset index
    duplicate_cols = ["id"] if "id" in df.columns else ["name", "artist"] if all(col in df.columns for col in ["name", "artist"]) else [df.columns[0]]
    
    initial_count = len(df)
    df.drop_duplicates(subset=duplicate_cols, inplace=True)
    df.reset_index(drop=True, inplace=True)
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        print(f"🧹 Removed {duplicate_count} duplicate rows")

    print(f"✅ Final dataset: {len(df)} valid tracks")

    if save_clean_copy:
        clean_path = csv_path.parent / f"{csv_path.stem}_clean.csv"
        df.to_csv(clean_path, index=False)
        print(f"💾 Cleaned CSV saved as: {clean_path}")

    if df.empty:
        raise ValueError("❌ After cleaning, no valid tracks remain.")

    return df


# ----------------------------------------------------------
# 🎧 Load Songs from CSV with Audio Features
# ----------------------------------------------------------
def load_songs_from_csv(csv_path=None, sp=None):
    """
    Load songs from CSV with their audio features.
    The 'sp' parameter is kept for compatibility but not used.
    """
    # Use default path if none provided
    if csv_path is None:
        if DEFAULT_CSV_PATH is None:
            raise FileNotFoundError(
                "❌ No CSV file found. Please:\n"
                "1. Place 'songs_normalize.csv' in your Recommender folder, OR\n"
                "2. Specify the full path when calling this function"
            )
        csv_path = DEFAULT_CSV_PATH
    
    print(f"📁 Loading songs from: {csv_path}")
    
    try:
        # ✅ Step 1: Validate and clean the CSV file
        df = validate_and_clean_csv(csv_path, save_clean_copy=False)
        
        # ✅ Step 2: Ensure we have the required audio feature columns
        audio_feature_columns = [
            'danceability', 'energy', 'key', 'loudness', 'mode', 
            'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'valence', 'tempo', 'duration_ms'
        ]
        
        # Check which audio features are available in the CSV
        available_features = [col for col in audio_feature_columns if col in df.columns]
        missing_features = [col for col in audio_feature_columns if col not in df.columns]
        
        if missing_features:
            print(f"⚠️ Missing audio features in CSV: {missing_features}")
        
        print(f"✅ Available audio features: {available_features}")
        
        if not available_features:
            # If no standard features, use any numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            non_feature_cols = ['id', 'duration_ms', 'year', 'popularity']  # Exclude these
            available_features = [col for col in numeric_cols if col not in non_feature_cols]
            print(f"🔧 Using alternative numeric features: {available_features}")
        
        if not available_features:
            raise ValueError("❌ No suitable features found in the CSV file for recommendations.")
        
        print(f"✅ Successfully loaded {len(df)} tracks with {len(available_features)} features from CSV")
        
        # ✅ IMPORTANT: Make sure we return the DataFrame, not an integer
        return df
        
    except Exception as e:
        print(f"❌ Error in load_songs_from_csv: {e}")
        raise  # Re-raise the exception so callers can handle it


# ----------------------------------------------------------
# 🔐 Return Authenticated Spotify Client (for UI purposes)
# ----------------------------------------------------------
def get_authenticated_spotify(sp_client):
    """Return authenticated Spotify client instance (for UI/login purposes)."""
    return sp_client






