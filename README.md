
# Spotify Music Recommender System 🎵

A machine learning-powered music recommendation system that suggests songs based on audio features and user preferences using Spotify's Web API.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-orange)
![Spotify API](https://img.shields.io/badge/Spotify-API-brightgreen)

## ✨ Features

- **Smart Recommendations**: Content-based filtering using audio features
- **Spotify Integration**: Direct connection to Spotify's extensive music database
- **Audio Analysis**: Utilizes tempo, danceability, energy, and other musical attributes
- **User-Friendly Interface**: Easy-to-use web interface or command-line tool
- **Personalized Suggestions**: Recommendations tailored to individual music tastes

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/MamilaGun23/Spotify-music-recommender-system.git
cd Spotify-music-recommender-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Spotify API credentials**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app and get your Client ID and Client Secret
   - Create a `.env` file in the project root:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### Usage

**Run the application:**
```bash
python app.py
```

**Or use the Jupyter notebooks for development:**
```bash
jupyter notebook notebooks/exploration.ipynb
```

## 📁 Project Structure

```
Spotify-music-recommender-system/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
├── src/                  # Source code modules
│   ├── spotify_api.py    # Spotify API interactions
│   ├── data_processing.py # Data cleaning and preparation
│   ├── recommender.py    # Recommendation algorithms
│   └── utils.py          # Utility functions
├── notebooks/            # Jupyter notebooks for exploration
│   ├── data_exploration.ipynb
│   └── model_development.ipynb
├── data/                 # Data storage
│   ├── raw/             # Raw data files
│   └── processed/       # Processed data
├── tests/               # Test cases
└── assets/              # Images and documentation assets
```

## 🔧 Configuration

### Spotify API Setup

1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in app name and description
4. Add `http://localhost:8888/callback` to redirect URIs
5. Copy Client ID and Client Secret to your `.env` file

### Environment Variables

Create a `.env` file with the following variables:
```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=http://localhost:8888/callback
```

## 🎯 How It Works

1. **Data Collection**: Fetches track data and audio features from Spotify API
2. **Feature Engineering**: Processes audio characteristics (tempo, energy, danceability, etc.)
3. **Similarity Calculation**: Uses cosine similarity or other ML algorithms
4. **Recommendation Generation**: Suggests songs based on feature similarity

### Recommendation Algorithms

- **Content-Based Filtering**: Recommends songs similar to ones you already like
- **Audio Feature Analysis**: Uses Spotify's audio features for precise matching
- **Collaborative Filtering** (Planned): User-based recommendations

## 📊 Features Used for Recommendations

- **Acousticness**: Confidence measure of whether track is acoustic
- **Danceability**: How suitable a track is for dancing
- **Energy**: Perceived intensity and activity
- **Instrumentalness**: Predicts whether track contains no vocals
- **Liveness**: Detects presence of audience in recording
- **Loudness**: Overall loudness in decibels
- **Speechiness**: Detects presence of spoken words
- **Tempo**: Overall estimated tempo in BPM
- **Valence**: Musical positiveness conveyed by track

## 🛠️ Technologies Used

- **Python 3.8+**
- **Spotipy** - Spotify Web API wrapper
- **Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **NumPy** - Numerical computing
- **Matplotlib/Seaborn** - Data visualization
- **Jupyter** - Interactive development

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Spotify for providing the comprehensive Web API
- Spotipy library developers for the excellent Python wrapper
- Machine learning community for open-source algorithms and tools



---

