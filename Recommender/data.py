"""Portable CSV loading. No Spotify requests or writes during normal loading."""
import os
from pathlib import Path

import pandas as pd

from Recommender.features import validate_features

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV_PATH = BASE_DIR / "Recommender" / "songs_normalize.csv"


def get_default_csv_path():
    configured = Path(os.getenv("SONGS_CSV_PATH", str(DEFAULT_CSV_PATH)))
    return configured if configured.is_absolute() else BASE_DIR / configured


def validate_and_clean_csv(csv_path, save_clean_copy=False):
    path = Path(csv_path)
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError("Songs CSV missing. Set SONGS_CSV_PATH or restore Recommender/songs_normalize.csv.") from None
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError):
        raise ValueError("Songs CSV must be a readable, nonempty UTF-8 table.") from None
    if df.empty:
        raise ValueError("Songs CSV has no tracks.")
    if not {"song", "artist"}.issubset(df.columns):
        raise ValueError("Songs CSV requires song and artist columns.")
    for col in ("song", "artist"):
        if df[col].isna().any() or df[col].astype(str).str.strip().eq("").any():
            raise ValueError(f"Songs CSV contains missing {col} values.")
        df[col] = df[col].astype(str).str.strip()
    # Preserve original row identity, including repeated title/artist pairs.
    df = df.reset_index(drop=True)
    df["row_id"] = df.index
    values = validate_features(df)
    for column in values:
        df[column] = values[column]
    if save_clean_copy:
        df.to_csv(path.with_name(f"{path.stem}_clean.csv"), index=False)
    return df


def load_songs_from_csv(csv_path=None, sp=None):
    """The legacy sp argument is unused: features always come from the CSV."""
    return validate_and_clean_csv(csv_path if csv_path is not None else get_default_csv_path())


def get_authenticated_spotify(sp_client):
    return sp_client
