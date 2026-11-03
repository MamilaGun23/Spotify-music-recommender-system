"""Resolve CSV tracks through Spotify search, then create a private playlist."""
import spotipy


class PlaylistError(RuntimeError):
    """Recoverable playlist failure."""


def search_spotify_uri(sp: spotipy.Spotify, track_name: str, artist_name: str | None = None):
    query = f"track:{track_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    try:
        results = sp.search(q=query, type="track", limit=1)
    except Exception:
        raise PlaylistError("Spotify search failed; no playlist was created.") from None
    items = (results or {}).get("tracks", {}).get("items", [])
    return items[0]["uri"] if items else None


def create_playlist_from_selected_songs(sp, user_id, playlist_name, description, selected_songs_df):
    if not playlist_name.strip() or selected_songs_df.empty:
        raise PlaylistError("Choose tracks and provide a playlist name.")
    # Resolve before creating: no empty orphan playlist on failed search.
    uris = []
    for row in selected_songs_df.itertuples():
        uri = search_spotify_uri(sp, row.song, row.artist)
        if uri is None:
            raise PlaylistError("At least one selected track was not found; no playlist was created.")
        uris.append(uri)
    try:
        playlist = sp.user_playlist_create(
            user=user_id, name=playlist_name, public=False, description=description,
        )
        for offset in range(0, len(uris), 100):
            sp.playlist_add_items(playlist_id=playlist["id"], items=uris[offset:offset + 100])
        return playlist["external_urls"]["spotify"]
    except Exception:
        raise PlaylistError("Spotify playlist operation failed; check your account before retrying (a partial playlist may exist).") from None


def create_playlist_from_recommendations(sp, user_id, base_song, rec_df):
    return create_playlist_from_selected_songs(
        sp, user_id, f"Recommended from {base_song}",
        f"CSV audio-feature recommendations based on {base_song}.", rec_df,
    )
