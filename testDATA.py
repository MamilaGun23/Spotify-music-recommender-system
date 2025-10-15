import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-library-read"
))

# Test with a single track ID from your dataset
track_id = "2AmjYouvSZkOnEoZZ1CD6u"  
try:
    features = sp.audio_features([track_id])
    print(features)
except Exception as e:
    print("Error:", e)
