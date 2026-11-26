"""Plain data types shared across providers and services."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Movie:
    id: str
    title: str
    year: str
    overview: str
    poster_url: str | None


@dataclass(frozen=True)
class Review:
    id: str
    author: str
    text: str
