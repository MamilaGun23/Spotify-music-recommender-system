"""Local desktop OAuth with a fresh in-memory cache for every login.

The loopback callback opens on the server machine; this is not hosted multiuser
OAuth. No shared disk token cache, import-time validation or credential logging.
"""
import os
from pathlib import Path
from secrets import token_urlsafe
from urllib.parse import urlparse

import spotipy
from dotenv import load_dotenv
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "playlist-modify-private"


class AuthenticationError(RuntimeError):
    """Recoverable authentication/configuration failure, safe to show in the UI."""


def get_spotify_client():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    names = ("SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI")
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise AuthenticationError("Missing configuration: " + ", ".join(missing))
    try:
        uri = urlparse(os.environ["SPOTIPY_REDIRECT_URI"])
        valid_uri = uri.scheme == "http" and uri.hostname == "127.0.0.1" and uri.port
    except ValueError:
        valid_uri = False
    if not valid_uri:
        raise AuthenticationError("Use an explicit local callback such as http://127.0.0.1:8888/callback.")
    try:
        manager = SpotifyOAuth(
            client_id=os.environ[names[0]], client_secret=os.environ[names[1]],
            redirect_uri=os.environ[names[2]], scope=SCOPE,
            state=token_urlsafe(32), cache_handler=MemoryCacheHandler(),
            show_dialog=True,
        )
        client = spotipy.Spotify(auth_manager=manager, requests_timeout=15)
        client.current_user()
        return client
    except Exception:
        raise AuthenticationError("Spotify login failed. Check app configuration, access and callback, then retry.") from None
