"""Shapes domain objects into the JSON the frontend consumes."""
from __future__ import annotations

from app.domain.emotions import DISPLAY_NAMES, MAJOR_EMOTIONS
from app.domain.entities import Movie
from app.services.film_service import FilmReport


def movie_json(movie: Movie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "overview": movie.overview,
        "posterUrl": movie.poster_url,
    }


def report_json(report: FilmReport) -> dict:
    analysis = report.analysis
    return {
        "movie": movie_json(report.movie),
        "source": report.source,
        "reviewsFetched": report.fetched_reviews,
        "reviewsScored": len(analysis.reviews),
        "reviewsSkipped": analysis.skipped_reviews,
        "neutralShare": round(analysis.neutral_share, 4),
        "final": {
            "key": analysis.final,
            "label": DISPLAY_NAMES[analysis.final],
            "score": round(next(e.score for e in analysis.emotions if e.key == analysis.final), 4),
        },
        "emotions": [
            {
                "key": e.key,
                "label": DISPLAY_NAMES[e.key],
                "score": round(e.score, 4),
                "strength": e.strength,
                "ledReviews": e.led_reviews,
            }
            for e in analysis.emotions
        ],
        "reviews": [
            {
                "id": r.review_id,
                "author": r.author,
                "text": r.text,
                "dominant": r.dominant,
                "scores": {k: round(r.scores[k], 4) for k in MAJOR_EMOTIONS},
            }
            for r in analysis.reviews
        ],
    }
