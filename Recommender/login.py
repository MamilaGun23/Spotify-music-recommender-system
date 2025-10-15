# Recommender/login.py

import os
import streamlit as st
from Recommender.auth import get_spotify_client

def render_login_page():
    """
    Renders the Spotify login page and handles authentication.
    Returns authenticated Spotify client and user info if successful.
    """
    st.set_page_config(page_title="Spotify Login", page_icon="🎧", layout="centered")
    
    st.title("🎧 Welcome to Music Recommender")
    st.markdown("""
    ### Connect your Spotify account to get started
    
    This app will:
    - 📊 Analyze your music taste from our extensive dataset
    - 🎵 Recommend similar songs you'll love
    - 🎧 Create personalized playlists on your Spotify account
    
    *Note: We use your Spotify account only for playlist creation and authentication.*
    """)
    
    # Spotify branding
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg", 
                width=200, use_column_width=True)
    
    st.markdown("---")
    
    # Login button
    if st.button("🎵 Login with Spotify", type="primary", use_container_width=True):
        with st.spinner("Connecting to Spotify..."):
            try:
                sp = get_spotify_client()
                current_user = sp.current_user() # type: ignore
                user_id = current_user.get("id", "Unknown User") # type: ignore
                display_name = current_user.get("display_name") or user_id # type: ignore
                
                st.success(f"✅ Successfully logged in as **{display_name}**")
                st.session_state['sp'] = sp
                st.session_state['user_id'] = user_id
                st.session_state['display_name'] = display_name
                st.session_state['authenticated'] = True
                
                # Show success and navigation
                st.balloons()
                st.info("🎉 Authentication successful! You can now use all features of the app.")
                
                return sp, user_id, display_name
                
            except Exception as e:
                st.error(f"❌ Login failed: {str(e)}")
                st.info("💡 Please check your credentials and try again.")
                return None, None, None
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<small>🔒 Your Spotify data is handled securely and never stored on our servers.</small>",
        unsafe_allow_html=True
    )
    
    return None, None, None

def check_authentication():
    """
    Check if user is already authenticated in session state.
    Returns Spotify client and user info if authenticated.
    """
    if st.session_state.get('authenticated', False):
        return (
            st.session_state.get('sp'),
            st.session_state.get('user_id'),
            st.session_state.get('display_name')
        )
    return None, None, None

def logout():
    """
    Clear authentication from session state.
    """
    for key in ['sp', 'user_id', 'display_name', 'authenticated']:
        if key in st.session_state:
            del st.session_state[key]