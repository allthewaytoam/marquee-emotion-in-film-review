import unittest

from app.config import Settings
from app.errors import ConfigurationError, MovieNotFound, ProviderError
from app.providers import build_provider
from app.providers.tmdb import TMDBProvider


class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status_code, self._payload, self.ok = status, payload or {}, status < 400

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


class TMDBTests(unittest.TestCase):
    def test_search_maps_movies(self):
        payload = {"results": [{"id": 7, "title": "Heat", "release_date": "1995-12-15", "poster_path": "/p.jpg", "overview": "x"}]}
        session = FakeSession([FakeResponse(200, payload)])
        movie = TMDBProvider("key", session=session).list_movies("heat")[0]
        self.assertEqual((movie.id, movie.year), ("7", "1995"))
        self.assertTrue(movie.poster_url.endswith("/p.jpg"))
        self.assertEqual(session.calls[0][1]["params"]["api_key"], "key")

    def test_reviews_paginate_until_limit(self):
        page = lambda n: FakeResponse(200, {"total_pages": 3, "results": [{"id": f"{n}{i}", "author": "a", "content": "text"} for i in range(2)]})
        session = FakeSession([page(1), page(2), page(3)])
        reviews = TMDBProvider("key", session=session).get_reviews("1", limit=3)
        self.assertEqual(len(reviews), 3)
        self.assertEqual(len(session.calls), 2)

    def test_bearer_token_used_when_given(self):
        session = FakeSession([FakeResponse(200, {"results": []})])
        TMDBProvider(access_token="tok", session=session).list_movies()
        kwargs = session.calls[0][1]
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer tok")
        self.assertNotIn("api_key", kwargs["params"])

    def test_error_statuses(self):
        for status, exc in ((404, MovieNotFound), (401, ProviderError), (500, ProviderError)):
            with self.subTest(status=status), self.assertRaises(exc):
                TMDBProvider("k", session=FakeSession([FakeResponse(status)])).get_movie("1")

    def test_missing_credentials_fail_at_startup(self):
        settings = Settings.from_env().__class__(**{**Settings.from_env().__dict__, "tmdb_api_key": "", "tmdb_access_token": ""})
        with self.assertRaises(ConfigurationError):
            build_provider(settings)


class TokenDetectionTests(unittest.TestCase):
    def test_bearer_token_in_key_field_is_recognised(self):
        import os
        from unittest import mock

        with mock.patch.dict(os.environ, {"TMDB_API_KEY": "eyJabc.def.ghi", "TMDB_ACCESS_TOKEN": ""}):
            settings = Settings.from_env()
        self.assertEqual((settings.tmdb_api_key, settings.tmdb_access_token), ("", "eyJabc.def.ghi"))
