"""The Movie Database (TMDB) v3 client."""
from __future__ import annotations

import requests

from app.domain.entities import Movie, Review
from app.errors import MovieNotFound, ProviderError

_API = "https://api.themoviedb.org/3"
_POSTER = "https://image.tmdb.org/t/p/w342"


class TMDBProvider:
    name = "tmdb"

    def __init__(
        self,
        api_key: str = "",
        access_token: str = "",
        timeout: float = 8.0,
        session: requests.Session | None = None,
    ):
        self._api_key = api_key
        self._access_token = access_token
        self._timeout = timeout
        self._session = session or requests.Session()

    def list_movies(self, query: str = "", page: int = 1) -> list[Movie]:
        query = query.strip()
        if query:
            payload = self._get("/search/movie", query=query, page=page, include_adult="false")
        else:
            payload = self._get("/movie/popular", page=page)
        return [self._to_movie(item) for item in payload.get("results", [])]

    def get_movie(self, movie_id: str) -> Movie:
        return self._to_movie(self._get(f"/movie/{movie_id}"))

    def get_reviews(self, movie_id: str, limit: int) -> list[Review]:
        reviews: list[Review] = []
        page, total_pages = 1, 1
        while page <= total_pages and len(reviews) < limit:
            payload = self._get(f"/movie/{movie_id}/reviews", page=page)
            total_pages = payload.get("total_pages", 1)
            for item in payload.get("results", []):
                if item.get("content"):
                    reviews.append(Review(str(item["id"]), item.get("author") or "Anonymous", item["content"]))
            page += 1
        return reviews[:limit]

    def _get(self, path: str, **params) -> dict:
        headers = {"Accept": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        else:
            params["api_key"] = self._api_key
        try:
            response = self._session.get(f"{_API}{path}", params=params, headers=headers, timeout=self._timeout)
        except requests.RequestException as exc:
            raise ProviderError("Could not reach TMDB. Check the network connection and try again.") from exc

        if response.status_code == 404:
            raise MovieNotFound("TMDB has no film with that id.")
        if response.status_code in (401, 403):
            raise ProviderError("TMDB rejected the API credentials. Check TMDB_API_KEY or TMDB_ACCESS_TOKEN.")
        if not response.ok:
            raise ProviderError(f"TMDB responded with status {response.status_code}.")
        return response.json()

    @staticmethod
    def _to_movie(item: dict) -> Movie:
        poster = item.get("poster_path")
        return Movie(
            id=str(item["id"]),
            title=item.get("title") or item.get("original_title") or "Untitled",
            year=(item.get("release_date") or "")[:4],
            overview=item.get("overview") or "",
            poster_url=f"{_POSTER}{poster}" if poster else None,
        )
