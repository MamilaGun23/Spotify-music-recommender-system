"""
Streamlit app: Music Recommender with Dedicated UI
"""

import streamlit as st
from Recommender.ui import SpotifyUI
from Recommender.data import load_songs_from_csv
from Recommender.recommend import recommend_from_song, get_available_songs, get_song_mapping
from Recommender.playlist_utils import create_playlist_from_selected_songs
from Recommender.login import render_login_page, check_authentication, logout
from Recommender.analytics import track_recommendation

def main():
    # Initialize UI
    ui = SpotifyUI()
    
    # Authentication
    sp, user_id, display_name = check_authentication()
    if not sp:
        sp, user_id, display_name = render_login_page()
        if not sp:
            st.stop()

    # Load data
    try:
        with ui.show_loading_message("🎵 Loading the CSV catalogue..."):
            df = load_songs_from_csv(sp=sp)
        ui.show_success_message(f"✅ Loaded {len(df)} songs from the CSV catalogue")
    except Exception as e:
        ui.show_error_message(f"❌ Error loading songs: {e}")
        st.stop()

    # Sidebar
    logout_requested = ui.render_sidebar(display_name, df)
    if logout_requested:
        logout()
        st.rerun()

    # Main content
    ui.render_main_header()
    
    # Get available songs for dropdowns
    available_songs = get_available_songs(df)
    song_mapping = get_song_mapping(df)
    
    # Recommendation section
    selected_song_name, _ = ui.render_recommendation_section(df, available_songs, song_mapping)
    
    # Handle recommendations
    if selected_song_name is not None:
        with ui.show_loading_message("🔍 Analyzing music patterns..."):
            recs = recommend_from_song(selected_song_name, df)
            selected_label = next(label for label, row_id in song_mapping.items() if row_id == selected_song_name)
            track_recommendation(selected_label, recs, st.session_state)
        
        if not recs.empty:
            st.session_state.recommendations = recs
            st.session_state.selected_song = selected_label
            ui.show_success_message(f"🎉 Found {len(recs)} similar songs!")
        else:
            ui.show_warning_message("🤔 No similar songs found. Try a different song!")
    
    # Display recommendations if available
    if 'recommendations' in st.session_state and not st.session_state.recommendations.empty:
        ui.render_recommendation_results(
            st.session_state.recommendations, 
            st.session_state.get('selected_song', ''), 
            sp, 
            user_id
        )

    # Custom playlist section
    selected_songs, playlist_name, playlist_desc = ui.render_custom_playlist_section(
        df, available_songs, sp, user_id
    )
    
    if selected_songs and playlist_name:
        if not selected_songs:
            ui.show_warning_message("⚠️ Please select at least one song for your playlist.")
        elif not playlist_name.strip():
            ui.show_warning_message("⚠️ Please enter a playlist name.")
        else:
            try:
                with ui.show_loading_message("Creating your custom playlist..."):
                    selected_ids = [song_mapping[song] for song in selected_songs]
                    selected_songs_df = df.set_index('row_id', drop=False).loc[selected_ids]
                    
                    playlist_url = create_playlist_from_selected_songs(
                        sp, user_id, playlist_name, playlist_desc, selected_songs_df # type: ignore
                    )
                
                ui.show_success_message(f"✅ Custom playlist '{playlist_name}' created!")
                ui.show_celebration()
                st.markdown(f"🎵 [Open Playlist on Spotify]({playlist_url})")
                
            except Exception as e:
                ui.show_error_message(f"❌ Failed to create playlist: {e}")

    # Footer
    ui.render_footer()

if __name__ == "__main__":
    main()
