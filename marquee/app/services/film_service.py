"""Orchestrates review fetching and emotion analysis for one film."""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import Movie
from app.errors import NoReviewsError
from app.providers.base import ReviewProvider
from app.services.analysis import EmotionAnalyzer, FilmAnalysis
from app.services.cache import TTLCache


@dataclass(frozen=True)
class FilmReport:
    movie: Movie
    analysis: FilmAnalysis
    fetched_reviews: int
    source: str


class FilmService:
    def __init__(
        self,
        provider: ReviewProvider,
        analyzer: EmotionAnalyzer,
        max_reviews: int,
        cache: TTLCache[FilmReport],
    ):
        self.provider = provider
        self._analyzer = analyzer
        self._max_reviews = max_reviews
        self._cache = cache

    def report_for(self, movie_id: str) -> FilmReport:
        cached = self._cache.get(movie_id)
        if cached is not None:
            return cached

        movie = self.provider.get_movie(movie_id)
        reviews = self.provider.get_reviews(movie_id, self._max_reviews)
        if not reviews:
            raise NoReviewsError(f"'{movie.title}' has no written reviews to analyse yet.")

        analysis = self._analyzer.analyze(reviews)
        if not analysis.reviews:
            raise NoReviewsError("None of the reviews contained text the model could score.")

        report = FilmReport(movie, analysis, len(reviews), self.provider.name)
        self._cache.set(movie_id, report)
        return report
