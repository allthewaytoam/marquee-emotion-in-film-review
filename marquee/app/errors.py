"""Application errors. Each carries the HTTP status and a stable machine code."""


class AppError(Exception):
    status = 500
    code = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ModelLoadError(AppError):
    code = "model_unavailable"


class ProviderError(AppError):
    status = 502
    code = "review_source_error"


class MovieNotFound(AppError):
    status = 404
    code = "movie_not_found"


class NoReviewsError(AppError):
    status = 422
    code = "no_reviews"


class ConfigurationError(AppError):
    code = "configuration_error"
