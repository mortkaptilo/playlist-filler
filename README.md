# Playlist Filler

A music recommendation system that suggests tracks based on a playlist you provide.
The backend uses three machine learning methods to generate recommendations and combines their results into a single ranked list.

## How it works

You search for tracks and add them to a seed playlist. When you click "Fill Playlist", the backend runs three recommendation models on your selection:

- **Item-based cosine similarity** — compares audio features (energy, tempo, danceability, etc.) between your seed tracks and all other tracks in the dataset. Tracks with similar audio profiles score higher.

- **User-based cosine similarity** — treats your seed playlist as a virtual user, finds real users in the dataset with similar listening habits, and recommends tracks they listened to.

- **SVD (matrix factorisation)** — decomposes the user-item interaction matrix into latent factors. Your seed playlist is projected into this latent space and scored against all tracks.

Each method produces a score for candidate tracks. Scores are normalised and averaged across all three methods to produce the final ranking.

## Dataset

The project uses the [Last.fm dataset](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm) which contains track audio features and user listening history.

Place the following files in `datasets/` before training:

```
datasets/
  music_info.csv
  user_listening_history.csv
```

## Project structure

```
playlist-filler/
  backend/
    app/              FastAPI application
    training/         Training scripts
    models/           Saved model artifacts (generated after training)
    requirements.txt
  front/              React + TypeScript frontend
  datasets/           Raw CSV data (not tracked in git)
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd front
npm install
```

## Training

Run the full training pipeline from the `backend/` directory. This reads the CSVs, builds the models, and writes artifacts to `backend/models/`.

```bash
cd backend
source venv/bin/activate
python -m training.train_all
```

To use a subset of users for faster training:

```bash
python -m training.train_all --max-users 50000
```

Training on the full dataset takes around 30 seconds.

## Running

Start the backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Start the frontend:

```bash
cd front
npm run dev
```

Open `http://localhost:5173` in your browser.

## Tech stack

- Python, FastAPI, scikit-learn, scipy, pandas, numpy
- React, TypeScript, Tailwind CSS, Jotai, Vite
