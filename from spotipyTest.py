from spotipy.oauth2 import SpotifyOAuth
import spotipy

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_ID",
    client_secret="YOUR_SECRET",
    redirect_uri="http://127.0.0.1:8501/",
    scope="user-library-read"
))

print(sp.audio_features(["2AmjYouvSZkOnEoZZ1CD6u"]))
