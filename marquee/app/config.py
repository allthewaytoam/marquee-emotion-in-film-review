"""Runtime configuration, read once from the environment."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _path(name: str, default: str) -> Path:
    raw = Path(os.getenv(name, default))
    return raw if raw.is_absolute() else ROOT / raw


@dataclass(frozen=True)
class Settings:
    model_path: Path
    vectorizer_path: Path
    tmdb_api_key: str
    tmdb_access_token: str
    max_reviews: int
    score_temperature: float
    cache_ttl_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        key = os.getenv("TMDB_API_KEY", "").strip()
        token = os.getenv("TMDB_ACCESS_TOKEN", "").strip()
        if key.startswith("eyJ"):  # a v4 bearer token pasted into the key field
            key, token = "", token or key
        return cls(
            model_path=_path("MODEL_PATH", "models/best_emotion_detection_model.pkl"),
            vectorizer_path=_path("VECTORIZER_PATH", "models/tfidf_vectorizer.pkl"),
            tmdb_api_key=key,
            tmdb_access_token=token,
            max_reviews=int(os.getenv("MAX_REVIEWS", "30")),
            score_temperature=float(os.getenv("SCORE_TEMPERATURE", "2.0")),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "900")),
        )

    @property
    def has_tmdb_credentials(self) -> bool:
        return bool(self.tmdb_api_key or self.tmdb_access_token)
