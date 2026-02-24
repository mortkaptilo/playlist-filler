from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DATASETS_DIR = PROJECT_DIR / "datasets"
MODELS_DIR = BACKEND_DIR / "models"

MUSIC_INFO_CSV = DATASETS_DIR / "music_info.csv"
USER_HISTORY_CSV = DATASETS_DIR / "user_listening_history.csv"

# Audio features used for item-based cosine similarity
AUDIO_FEATURES = [
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo", "time_signature",
]

SVD_N_COMPONENTS = 50
SVD_RANDOM_STATE = 42

# Limit users loaded from the history CSV to speed up training.
# Set to None to use the full dataset.
MAX_USERS: int | None = None
