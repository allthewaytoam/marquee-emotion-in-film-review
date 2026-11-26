"""Contract every review source implements."""
from __future__ import annotations

from typing import Protocol

from app.domain.entities import Movie, Review


class ReviewProvider(Protocol):
    name: str

    def list_movies(self, query: str = "", page: int = 1) -> list[Movie]:
        """Search by title, or return a popular list when `query` is empty."""

    def get_movie(self, movie_id: str) -> Movie: ...

    def get_reviews(self, movie_id: str, limit: int) -> list[Review]: ...
