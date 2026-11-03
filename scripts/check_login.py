"""Optional manual check; never imported or run by the offline test suite."""
from Recommender.auth import AuthenticationError, get_spotify_client
from Recommender.data import load_songs_from_csv
from Recommender.playlist_utils import search_spotify_uri


if __name__ == "__main__":
    try:
        client = get_spotify_client()
        print("PASS: live Spotify login and current-user profile.")
        row = load_songs_from_csv().iloc[0]
        uri = search_spotify_uri(client, row.song, row.artist)
        if not uri:
            raise RuntimeError("The catalogue track was not returned by Spotify search.")
        print("PASS: live Spotify track search.")
        print("Playlist creation was not exercised by this read-only check.")
    except AuthenticationError as error:
        print(f"BLOCKED: {error}")
        raise SystemExit(2) from None
    except Exception:
        print("FAIL: live search or catalogue validation. Check account access and configuration.")
        raise SystemExit(1) from None
