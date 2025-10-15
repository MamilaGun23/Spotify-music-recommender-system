# pages/analytics.py - SIMPLE WRAPPER PAGE

import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from Recommender
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Recommender.data import load_songs_from_csv, DEFAULT_CSV_PATH
from Recommender.analytics import show_analytics_dashboard
from Recommender.login import check_authentication

# Page configuration
st.set_page_config(
    page_title="Music Analytics",
    page_icon="📊", 
    layout="wide"
)

def main():
    st.title("📊 Music Recommender Analytics")
    
    # Authentication check
    sp, user_id, display_name = check_authentication()
    if not sp:
        st.error("🔐 Please log in on the main page to view analytics.")
        st.stop()
    
    st.success(f"✅ Logged in as **{display_name}**")
    
    try:
        # Load the data
        with st.spinner("📥 Loading dataset..."):
            df = load_songs_from_csv(DEFAULT_CSV_PATH, sp)
        
        # Show quick dataset info
        with st.expander("🔍 Dataset Overview"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Songs", len(df))
            with col2:
                st.metric("Unique Artists", df['artist'].nunique())
            with col3:
                st.metric("Data Features", len(df.columns))
        
        # Initialize recommendations history if needed
        if 'recommendations_history' not in st.session_state:
            st.session_state.recommendations_history = []
            st.info("💡 No recommendation history yet. Generate some recommendations on the main page first!")
        
        # Show the full analytics dashboard
        show_analytics_dashboard(df, st.session_state.recommendations_history)
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("💡 Try going to the main page first to ensure the dataset loads properly.")

if __name__ == "__main__":
    main()