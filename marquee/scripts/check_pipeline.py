"""Verifies the model files, the backend wiring and the review source in one go.

    python -m scripts.check_pipeline
"""
from __future__ import annotations

import sys
import warnings

from app import create_app
from app.config import Settings


def step(label: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'pass' if ok else 'FAIL'}] {label}{(' - ' + detail) if detail else ''}")
    return ok


def main() -> int:
    settings = Settings.from_env()
    results = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            app = create_app(settings)
        except Exception as exc:
            step("Startup (model files and TMDB credentials)", False, str(exc))
            return 1
    results.append(step("Model and vectoriser load together", True))

    client = app.test_client()
    health = client.get("/api/health").get_json()
    results.append(step("Review source", health["source"] == "tmdb", health["source"]))

    movies = client.get("/api/movies").get_json()["movies"]
    results.append(step("Movie list returns films", bool(movies), f"{len(movies)} films"))
    if not movies:
        return 1

    response = client.get(f"/api/movies/{movies[0]['id']}/analysis")
    body = response.get_json()
    if response.status_code != 200:
        step("Analysis for first film", False, body["error"]["message"])
        return 1
    total = sum(e["score"] for e in body["emotions"])
    results.append(step("Analysis for first film", True, f"{body['movie']['title']} -> {body['final']['label']}"))
    results.append(step("Five emotion scores sum to 1", abs(total - 1) < 0.01, f"{total:.3f}"))
    results.append(step("Frontend files are served", client.get("/").status_code == 200))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
