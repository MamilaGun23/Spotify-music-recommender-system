# Recommender/ui.py

import streamlit as st

class SpotifyUI:
    """
    Dedicated UI class for handling all Streamlit UI components and styling.
    Centralizes all UI logic for maintainability and reusability.
    """
    
    def __init__(self):
        self.setup_page_config()
        self.inject_custom_css()
    
    def setup_page_config(self):
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title="🎧 Spotify Music Recommender",
            page_icon="🎵",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def inject_custom_css(self):
        """Inject custom CSS for Spotify-themed styling."""
        st.markdown("""
        <style>
            .main-header {
                font-size: 3rem;
                color: #1DB954;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: bold;
            }
            .section-header {
                font-size: 1.5rem;
                color: #1DB954;
                border-bottom: 2px solid #1DB954;
                padding-bottom: 0.5rem;
                margin-top: 2rem;
                font-weight: 600;
            }
            .recommendation-card {
                background-color: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                border-left: 4px solid #1DB954;
            }
            .sidebar-logo {
                text-align: center;
                margin-bottom: 1.5rem;
                padding: 1rem;
            }
            .spotify-green {
                color: #1DB954;
            }
            .metric-card {
                background: linear-gradient(135deg, #1DB954, #1ed760);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
            }
            .footer {
                text-align: center;
                color: #666;
                margin-top: 3rem;
                padding-top: 1rem;
                border-top: 1px solid #e0e0e0;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self, display_name, df=None):
        """
        Render the application sidebar with user info and navigation.
        
        Args:
            display_name (str): User's display name
            df (DataFrame, optional): Dataset for stats display
        """
        with st.sidebar:
            # Spotify Logo
            st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg", 
                    width=200, use_container_width=True)
            st.markdown('</div>')
            
            # User Welcome
            st.markdown("---")
            st.markdown(f"### 👋 Welcome, **{display_name}**!")
            
            # Quick Stats Section
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            self._render_sidebar_stats(df)
            
            # Navigation
            st.markdown("---")
            st.markdown("### 🎯 Navigation")
            if st.button("📊 Go to Analytics", use_container_width=True):
                st.switch_page("pages/analytics.py")
            
            # Logout
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                return True  # Signal logout
        return False
    
    def _render_sidebar_stats(self, df):
        """Render statistics in the sidebar."""
        if df is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Songs", len(df))
            with col2:
                st.metric("Unique Artists", df['artist'].nunique())
        else:
            st.info("📥 Load dataset to see stats")
    
    def render_main_header(self):
        """Render the main header section."""
        st.markdown('<h1 class="main-header">🎧 Music Recommender</h1>', unsafe_allow_html=True)
        st.markdown("Discover new music based on your taste using our AI-powered recommendation system!")
    
    def render_recommendation_section(self, df, available_songs, song_mapping):
        """
        Render the song recommendation section.
        
        Returns:
            tuple: (selected_song_name, recommendations_dataframe) if recommendations generated
        """
        st.markdown('<div class="section-header">🎶 Get Song Recommendations</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_song_display = st.selectbox(
                "Select a song you like:",
                options=available_songs,
                help="Choose a song to get similar recommendations"
            )
            selected_song_name = song_mapping[selected_song_display]
            
            if st.button("✨ Find Similar Songs", type="primary", use_container_width=True):
                return selected_song_name, None
        
        with col2:
            self._render_quick_stats(df)
        
        return None, None
    
    def _render_quick_stats(self, df):
        """Render quick stats in the recommendation section."""
        st.markdown("### 📈 Library Stats")
        st.metric("Songs in Library", len(df))
        st.metric("Artists", df['artist'].nunique())
    
    def render_recommendation_results(self, recs, selected_song_name, sp, user_id):
        """
        Render the recommendation results and playlist creation options.
        """
        if recs is not None and not recs.empty:
            st.markdown("---")
            st.markdown('<div class="section-header">🎵 Recommended Songs</div>', unsafe_allow_html=True)
            
            # Display recommendations table
            display_columns = self._get_display_columns(recs)
            st.dataframe(recs[display_columns], use_container_width=True, height=400)
            
            # Playlist creation
            self._render_playlist_creation(recs, selected_song_name, sp, user_id)
    
    def _get_display_columns(self, recs):
        """Determine which columns to display in recommendations."""
        display_columns = []
        if 'artist' in recs.columns:
            display_columns.append('artist')
        if 'song' in recs.columns:
            display_columns.append('song')
        if 'similarity' in recs.columns:
            display_columns.append('similarity')
        if 'spotify_link' in recs.columns:
            display_columns.append('spotify_link')
        return display_columns
    
    def _render_playlist_creation(self, recs, selected_song_name, sp, user_id):
        """Render playlist creation options."""
        from Recommender.playlist_utils import create_playlist_from_recommendations
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎧 Create Spotify Playlist", type="secondary", use_container_width=True):
                with st.spinner("Creating your playlist..."):
                    playlist_url = create_playlist_from_recommendations(
                        sp, user_id, selected_song_name, recs
                    )
                st.success("✅ Playlist created successfully!")
                st.markdown(f"🎵 [Open Playlist on Spotify]({playlist_url})")
    
    def render_custom_playlist_section(self, df, available_songs, sp, user_id):
        """Render the custom playlist creation section."""
        st.markdown("---")
        st.markdown('<div class="section-header">🛠️ Create Custom Playlist</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            selected_songs_for_playlist = st.multiselect(
                "Choose songs for your custom playlist:",
                options=available_songs,
                help="Select multiple songs to include in your custom playlist",
                max_selections=50
            )
        
        with col2:
            playlist_name = st.text_input("Playlist Name:", value="My Custom Mix")
            playlist_description = st.text_input(
                "Playlist Description:", 
                value="Created with Music Recommender 🎧"
            )
            
            if st.button("🛠️ Create Custom Playlist", use_container_width=True):
                return selected_songs_for_playlist, playlist_name, playlist_description
        
        return None, None, None
    
    def render_footer(self):
        """Render the application footer."""
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <p>Built with ❤️ using Streamlit & Spotify API</p>
            <p>Your music taste, amplified by AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_loading_message(self, message):
        """Display a loading message with spinner."""
        return st.spinner(message)
    
    def show_success_message(self, message):
        """Display a success message."""
        st.success(message)
    
    def show_error_message(self, message):
        """Display an error message."""
        st.error(message)
    
    def show_warning_message(self, message):
        """Display a warning message."""
        st.warning(message)
    
    def show_celebration(self):
        """Show celebration effects."""
        st.balloons()