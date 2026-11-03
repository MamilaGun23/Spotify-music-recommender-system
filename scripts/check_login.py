"""Optional manual check; never imported or run by the offline test suite."""
from Recommender.auth import get_spotify_client


if __name__ == "__main__":
    get_spotify_client()
    print("Spotify account login succeeded.")
