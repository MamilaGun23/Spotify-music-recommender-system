import os
import sys
import time
import spotipy
from pathlib import Path
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError


# === PROJECT CONFIG ===
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
CACHE_PATH = BASE_DIR / ".cache"

# === LOAD ENV ===
if not ENV_PATH.exists():
    raise FileNotFoundError(f"❌ Missing .env file at {ENV_PATH}")
print(f"🔍 Looking for .env at: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)
print("Loaded ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("Environment variables loaded.")

# === VALIDATE REQUIRED VARIABLES ===
REQUIRED_ENV_VARS = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"❌ Missing required environment variables: {', '.join(missing)}")


def get_spotify_client(
    retries: int = 3,
    delay: int = 3
):
    """
    Authenticate and return a Spotify client using OAuth2.
    Handles caching, refresh, and retry logic.

    Returns:
        spotipy.Spotify: Authenticated Spotify client.
    """

    # === REQUESTED SCOPES (FULL ACCESS FOR PERSONALIZATION & PLAYLISTS) ===
    scope = (
        "user-library-read "
        "user-read-recently-played "
        "user-top-read "
        "playlist-read-private "
        "playlist-read-collaborative "
        "playlist-modify-private "
        "playlist-modify-public "
        "user-read-playback-state "
        "user-modify-playback-state "
        "user-read-currently-playing "
        "user-read-email "
        "user-read-private"
    )

    for attempt in range(1, retries + 1):
        try:
            auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    cache_path=str(CACHE_PATH)
)

            sp = spotipy.Spotify(auth_manager=auth_manager)

            # ✅ Sanity check: ensure valid token
            current_user = sp.current_user()
            print(f"✅ Spotify authentication successful. Logged in as: {current_user.get('display_name', 'Unknown User')}") # type: ignore

            # 🎯 Debug: Display the active scopes for verification
            print("🎯 Active Spotify scopes:", auth_manager.scope)

            return sp

        except SpotifyOauthError as e:
            print(f"⚠️ Spotify OAuth error on attempt {attempt}: {e}")
            if attempt < retries:
                print(f"🔁 Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Failed after multiple attempts. Please verify credentials and redirect URI.")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Unexpected authentication error: {e}")
            sys.exit(1)


