from __future__ import annotations

from app.config import Settings
from app.errors import ConfigurationError
from app.providers.base import ReviewProvider
from app.providers.tmdb import TMDBProvider


def build_provider(settings: Settings) -> ReviewProvider:
    if not settings.has_tmdb_credentials:
        raise ConfigurationError(
            "No TMDB credentials found. Set TMDB_API_KEY (or TMDB_ACCESS_TOKEN) in .env "
            "or the host's environment variables. Free key: https://www.themoviedb.org/settings/api"
        )
    return TMDBProvider(settings.tmdb_api_key, settings.tmdb_access_token)
