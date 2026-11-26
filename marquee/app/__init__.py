"""Application factory."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from flask import Flask, send_from_directory

from app.api.routes import api
from app.config import ROOT, Settings
from app.providers import build_provider
from app.services.analysis import EmotionAnalyzer
from app.services.cache import TTLCache
from app.services.emotion_classifier import EmotionClassifier
from app.services.film_service import FilmService

WEB_DIR = ROOT / "web"


@dataclass(frozen=True)
class Services:
    classifier: EmotionClassifier
    films: FilmService


def create_app(settings: Settings | None = None, classifier=None, provider=None) -> Flask:
    """`classifier` and `provider` can be injected, which is how tests avoid
    touching the real model or the network."""
    load_dotenv(ROOT / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = settings or Settings.from_env()

    classifier = classifier or EmotionClassifier.from_paths(
        settings.vectorizer_path, settings.model_path, settings.score_temperature
    )
    provider = provider or build_provider(settings)
    films = FilmService(
        provider=provider,
        analyzer=EmotionAnalyzer(classifier),
        max_reviews=settings.max_reviews,
        cache=TTLCache(settings.cache_ttl_seconds),
    )

    app = Flask(__name__, static_folder=None)
    app.extensions["marquee"] = Services(classifier, films)
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return send_from_directory(WEB_DIR, "index.html")

    @app.get("/<path:asset>")
    def assets(asset: str):
        return send_from_directory(WEB_DIR, asset)

    return app
