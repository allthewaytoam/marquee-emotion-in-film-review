from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.api.serializers import movie_json, report_json
from app.errors import AppError

api = Blueprint("api", __name__, url_prefix="/api")


def _services():
    return current_app.extensions["marquee"]


@api.get("/health")
def health():
    services = _services()
    return jsonify(
        status="ok",
        source=services.films.provider.name,
        labels=list(services.classifier.labels),
    )


@api.get("/movies")
def movies():
    query = request.args.get("query", "")
    page = max(request.args.get("page", 1, type=int), 1)
    found = _services().films.provider.list_movies(query, page)
    return jsonify(movies=[movie_json(m) for m in found], source=_services().films.provider.name)


@api.get("/movies/<movie_id>/analysis")
def analysis(movie_id: str):
    return jsonify(report_json(_services().films.report_for(movie_id)))


@api.errorhandler(AppError)
def handle_app_error(error: AppError):
    current_app.logger.warning("%s: %s", error.code, error.message)
    return jsonify(error={"code": error.code, "message": error.message}), error.status
