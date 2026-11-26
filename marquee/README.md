# Marquee
# Required. Set either one. https://www.themoviedb.org/settings/api
TMDB_API_KEY=e5de29c645054a47dd738876327aed27
TMDB_ACCESS_TOKEN=

# Model artefacts
MODEL_PATH=models/best_emotion_detection_model.pkl
VECTORIZER_PATH=models/tfidf_vectorizer.pkl

# Reviews fetched per film, and how sharply LinearSVC margins are turned into shares.
MAX_REVIEWS=30
SCORE_TEMPERATURE=2.0
CACHE_TTL_SECONDS=900
