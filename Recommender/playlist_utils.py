# Recommender/playlist_utils.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

def create_playlist_from_recommendations(sp: spotipy.Spotify, user_id: str, base_song: str, rec_df):
    """
    Creates a new Spotify playlist with recommended songs.
    Since your CSV doesn't have Spotify URIs, we'll search for the songs.
    """
    playlist_name = f"Recommended from {base_song}"
    description = f"Songs recommended based on '{base_song}' using Music Recommender."

    # Create playlist
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=description
    )

    uris = []
    added_songs = []
    failed_songs = []
    
    # Search for each recommended song on Spotify
    for _, row in rec_df.iterrows():
        try:
            song_name = row['song'] if 'song' in row else 'Unknown Song'
            artist_name = row['artist'] if 'artist' in row else 'Unknown Artist'
            
            # Search for the song on Spotify
            query = f"track:{song_name} artist:{artist_name}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']: # type: ignore
                track_uri = results['tracks']['items'][0]['uri'] # type: ignore
                uris.append(track_uri)
                added_songs.append(f"{song_name} - {artist_name}")
            else:
                failed_songs.append(f"{song_name} - {artist_name}")
                
        except Exception as e:
            failed_songs.append(f"{song_name} - {artist_name} (Error: {str(e)})") # type: ignore
    
    if not uris:
        st.warning("No songs could be found on Spotify to add to playlist.")
        return None

    if not playlist or "id" not in playlist:
        st.error("Failed to create playlist. Please try again.")
        return None

    # Add tracks in batches
    batch_size = 100
    for i in range(0, len(uris), batch_size):
        batch_uris = uris[i:i + batch_size]
        sp.playlist_add_items(playlist_id=playlist["id"], items=batch_uris)

    # Show results
    st.success(f"✅ Playlist '{playlist_name}' created successfully!")
    st.write(f"🎵 Added {len(added_songs)} songs to playlist")
    
    if failed_songs:
        st.warning(f"⚠️ Could not find {len(failed_songs)} songs on Spotify:")
        for song in failed_songs:
            st.write(f"   - {song}")
    
    st.markdown(f"🎶 [Open Playlist on Spotify]({playlist['external_urls']['spotify']})")

    return playlist['external_urls']['spotify']

def create_playlist_from_selected_songs(sp: spotipy.Spotify, user_id: str, playlist_name: str, description: str, selected_songs_df):
    """
    Creates a new Spotify playlist from manually selected songs.
    Since your CSV doesn't have Spotify URIs, we'll search for the songs.
    """
    # Create playlist
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=description
    )

    uris = []
    added_songs = []
    failed_songs = []
    
    # Search for each song on Spotify
    for _, row in selected_songs_df.iterrows():
        try:
            song_name = row['song']
            artist_name = row['artist']
            
            # Search for the song on Spotify
            query = f"track:{song_name} artist:{artist_name}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']: # type: ignore
                track_uri = results['tracks']['items'][0]['uri'] # type: ignore
                uris.append(track_uri)
                added_songs.append(f"{song_name} - {artist_name}")
            else:
                failed_songs.append(f"{song_name} - {artist_name}")
                
        except Exception as e:
            failed_songs.append(f"{row['song']} - {row['artist']} (Error: {str(e)})")
    
    if not uris:
        st.warning("No songs could be found on Spotify to add to playlist.")
        return None

    if not playlist or "id" not in playlist:
        st.error("Failed to create playlist. Please try again.")
        return None

    # Add tracks in batches
    batch_size = 100
    for i in range(0, len(uris), batch_size):
        batch_uris = uris[i:i + batch_size]
        sp.playlist_add_items(playlist_id=playlist["id"], items=batch_uris)

    # Show results
    st.success(f"✅ Playlist '{playlist_name}' created successfully!")
    st.write(f"🎵 Added {len(added_songs)} songs to playlist")
    
    if failed_songs:
        st.warning(f"⚠️ Could not find {len(failed_songs)} songs on Spotify:")
        for song in failed_songs:
            st.write(f"   - {song}")
    
    st.markdown(f"🎶 [Open Playlist on Spotify]({playlist['external_urls']['spotify']})")

    return playlist['external_urls']['spotify']


def search_spotify_uri(sp: spotipy.Spotify, track_name: str, artist_name: str = None): # type: ignore
    """
    Search for a song on Spotify to get its URI.
    Useful if your CSV doesn't have Spotify URIs but has song names and artists.
    """
    try:
        query = f"track:{track_name}"
        if artist_name:
            query += f" artist:{artist_name}"
        
        results = sp.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']: # type: ignore
            return results['tracks']['items'][0]['uri'] # type: ignore
        else:
            return None
    except Exception as e:
        st.error(f"Error searching for {track_name}: {e}")
        return None