# Recommender/analytics.py

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import pairwise_distances
from sklearn.manifold import TSNE
import plotly.express as px
import plotly.graph_objects as go

def show_data_overview(df):
    """Show basic statistics and overview of the dataset."""
    st.header("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Songs", len(df))
    
    with col2:
        st.metric("Unique Artists", df['artist'].nunique() if 'artist' in df.columns else "N/A")
    
    with col3:
        st.metric("Audio Features", len(get_numeric_features(df)))
    
    with col4:
        avg_duration = df['duration_ms'].mean() / 60000 if 'duration_ms' in df.columns else 0
        st.metric("Avg Duration", f"{avg_duration:.2f} min")
    
    # Basic info
    st.subheader("Dataset Information")
    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    st.write(f"**Numeric columns:** {len(numeric_cols)}")
    st.write(f"**Categorical columns:** {len(categorical_cols)}")

def get_numeric_features(df):
    """Get numeric feature columns for analysis."""
    exclude_cols = ['artist', 'song', 'explicit', 'year', 'genre']
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [col for col in numeric_cols if col not in exclude_cols]

def show_audio_features_distribution(df):
    """Show distribution of audio features."""
    st.header("🎵 Audio Features Distribution")
    
    feature_cols = get_numeric_features(df)
    
    if not feature_cols:
        st.warning("No numeric audio features found in the dataset.")
        return
    
    # Select features to visualize
    selected_features = st.multiselect(
        "Select features to visualize:",
        options=feature_cols,
        default=feature_cols[:4] if len(feature_cols) >= 4 else feature_cols
    )
    
    if selected_features:
        # Create subplots
        cols = st.columns(2)
        for idx, feature in enumerate(selected_features):
            with cols[idx % 2]:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.hist(df[feature].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                ax.set_title(f'Distribution of {feature}')
                ax.set_xlabel(feature)
                ax.set_ylabel('Frequency')
                st.pyplot(fig)

def show_feature_correlations(df):
    """Show correlation matrix of audio features."""
    st.header("🔗 Feature Correlations")
    
    feature_cols = get_numeric_features(df)
    
    if len(feature_cols) < 2:
        st.warning("Need at least 2 numeric features for correlation analysis.")
        return
    
    # Calculate correlation matrix
    corr_matrix = df[feature_cols].corr()
    
    # Plot correlation heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, 
                annot=True, 
                cmap='coolwarm', 
                center=0,
                square=True,
                ax=ax)
    ax.set_title('Audio Features Correlation Matrix')
    st.pyplot(fig)
    
    # Show strongest correlations
    st.subheader("Strongest Correlations")
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append({
                'Feature 1': corr_matrix.columns[i],
                'Feature 2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })
    
    corr_df = pd.DataFrame(corr_pairs)
    corr_df['Abs Correlation'] = corr_df['Correlation'].abs()
    top_correlations = corr_df.nlargest(10, 'Abs Correlation')
    
    st.dataframe(top_correlations.style.background_gradient(subset=['Correlation'], cmap='coolwarm'))

def show_music_clusters(df):
    """Show clustering of songs based on audio features."""
    st.header("🎯 Music Clustering Analysis")
    
    feature_cols = get_numeric_features(df)
    
    if len(feature_cols) < 3:
        st.warning("Need at least 3 numeric features for clustering visualization.")
        return
    
    # Prepare data
    X = df[feature_cols].fillna(0)
    
    # t-SNE for dimensionality reduction
    with st.spinner("Performing dimensionality reduction..."):
        tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X)-1))
        X_embedded = tsne.fit_transform(X)
    
    # Create interactive plot
    plot_df = pd.DataFrame({
        'x': X_embedded[:, 0],
        'y': X_embedded[:, 1],
        'song': df['song'],
        'artist': df['artist']
    })
    
    fig = px.scatter(plot_df, x='x', y='y', hover_data=['song', 'artist'],
                     title='Song Clusters Based on Audio Features (t-SNE)',
                     labels={'x': 'Component 1', 'y': 'Component 2'})
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretation:**
    - Songs that are closer together in this plot have similar audio characteristics
    - Distinct clusters may represent different music genres or styles
    - Use this to understand the diversity of your music dataset
    """)

def show_recommendation_metrics(df, recommendations_history=None):
    """Show metrics about recommendation performance."""
    st.header("📈 Recommendation Performance")
    
    if recommendations_history:
        st.subheader("Recent Recommendations")
        for i, (song, recs) in enumerate(recommendations_history[-5:], 1):
            st.write(f"{i}. **{song}** → {len(recs)} recommendations")
    
    # Model quality metrics
    st.subheader("Model Quality Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Feature coverage
        feature_coverage = len(get_numeric_features(df)) / 12  # 12 is max typical features
        st.metric("Feature Coverage", f"{feature_coverage:.1%}")
    
    with col2:
        # Data quality
        missing_ratio = df[get_numeric_features(df)].isnull().sum().sum() / (len(df) * len(get_numeric_features(df)))
        st.metric("Data Quality", f"{(1-missing_ratio):.1%}")
    
    with col3:
        # Diversity score (based on feature variance)
        feature_vars = df[get_numeric_features(df)].var().mean()
        diversity_score = min(feature_vars * 100, 100)  # Normalized score
        st.metric("Music Diversity", f"{diversity_score:.0f}/100")

def show_artist_insights(df):
    """Show insights about artists in the dataset."""
    st.header("🎤 Artist Insights")
    
    if 'artist' not in df.columns:
        st.warning("Artist information not available in the dataset.")
        return
    
    # Top artists by song count
    artist_counts = df['artist'].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    artist_counts.plot(kind='barh', ax=ax, color='lightcoral')
    ax.set_title('Top 10 Artists by Number of Songs')
    ax.set_xlabel('Number of Songs')
    plt.tight_layout()
    st.pyplot(fig)
    
    # Artist audio characteristics
    st.subheader("Artist Audio Profiles")
    
    top_artists = artist_counts.index.tolist()[:5]
    feature_cols = get_numeric_features(df)
    
    if feature_cols:
        selected_feature = st.selectbox("Select feature to compare artists:", feature_cols)
        
        artist_means = df.groupby('artist')[selected_feature].mean().loc[top_artists]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        artist_means.plot(kind='bar', ax=ax, color='lightgreen')
        ax.set_title(f'Average {selected_feature} by Artist')
        ax.set_ylabel(selected_feature) # type: ignore
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

def show_analytics_dashboard(df, recommendations_history=None):
    """Main function to display the complete analytics dashboard."""
    
    st.title("📊 Music Recommender Analytics")
    
    # Create tabs for different analytics sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "🎵 Features", 
        "🔗 Correlations", 
        "🎯 Clusters", 
        "🎤 Artists"
    ])
    
    with tab1:
        show_data_overview(df)
        show_recommendation_metrics(df, recommendations_history)
    
    with tab2:
        show_audio_features_distribution(df)
    
    with tab3:
        show_feature_correlations(df)
    
    with tab4:
        show_music_clusters(df)
    
    with tab5:
        show_artist_insights(df)

def track_recommendation(base_song, recommendations, history_dict, max_history=10):
    """Track recommendation history for analytics."""
    if 'recommendations_history' not in history_dict:
        history_dict['recommendations_history'] = []
    
    history_dict['recommendations_history'].append((base_song, len(recommendations)))
    
    # Keep only recent history
    if len(history_dict['recommendations_history']) > max_history:
        history_dict['recommendations_history'] = history_dict['recommendations_history'][-max_history:]