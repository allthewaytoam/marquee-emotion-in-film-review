"""Turns reviews into per-review and film-level emotion scores."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

import numpy as np

from app.domain.emotions import (
    LABEL_TO_MAJOR,
    MAJOR_EMOTIONS,
    NON_EMOTION_LABELS,
    strength_of,
)
from app.domain.entities import Review
from app.errors import ModelLoadError
from app.services.text import clean_review, split_into_chunks


class DistributionModel(Protocol):
    labels: tuple[str, ...]

    def predict_distribution(self, texts: Sequence[str]) -> np.ndarray: ...


@dataclass(frozen=True)
class ReviewResult:
    review_id: str
    author: str
    text: str
    scores: dict[str, float]
    dominant: str
    neutral_share: float


@dataclass(frozen=True)
class EmotionSummary:
    key: str
    score: float
    strength: str
    led_reviews: int


@dataclass(frozen=True)
class FilmAnalysis:
    emotions: list[EmotionSummary]
    final: str
    neutral_share: float
    reviews: list[ReviewResult]
    skipped_reviews: int


class EmotionAnalyzer:
    def __init__(self, model: DistributionModel):
        self._model = model
        self._label_index = self._build_label_index(model.labels)

    @staticmethod
    def _build_label_index(labels: Sequence[str]) -> dict[str, list[int]]:
        """Column indices of the model output belonging to each major emotion."""
        index: dict[str, list[int]] = {key: [] for key in (*MAJOR_EMOTIONS, "_neutral")}
        for column, label in enumerate(labels):
            if label in NON_EMOTION_LABELS:
                index["_neutral"].append(column)
            elif label in LABEL_TO_MAJOR:
                index[LABEL_TO_MAJOR[label]].append(column)
            else:
                raise ModelLoadError(f"Model label '{label}' has no mapping in app/domain/emotions.py")
        return index

    def analyze(self, reviews: Sequence[Review]) -> FilmAnalysis:
        results = [r for r in map(self._score_review, reviews) if r is not None]
        skipped = len(reviews) - len(results)
        if not results:
            return FilmAnalysis([], "", 0.0, [], skipped)

        mean_scores = {k: float(np.mean([r.scores[k] for r in results])) for k in MAJOR_EMOTIONS}
        led = {k: sum(1 for r in results if r.dominant == k) for k in MAJOR_EMOTIONS}
        emotions = [
            EmotionSummary(k, mean_scores[k], strength_of(mean_scores[k]), led[k])
            for k in MAJOR_EMOTIONS
        ]
        final = max(emotions, key=lambda e: e.score).key
        neutral = float(np.mean([r.neutral_share for r in results]))
        return FilmAnalysis(emotions, final, neutral, results, skipped)

    def _score_review(self, review: Review) -> ReviewResult | None:
        text = clean_review(review.text)
        probs = self._model.predict_distribution(split_into_chunks(text))
        usable = probs[~np.isnan(probs).any(axis=1)] if len(probs) else probs
        if len(usable) == 0:
            return None

        mean = usable.mean(axis=0)
        grouped = {k: float(mean[self._label_index[k]].sum()) for k in MAJOR_EMOTIONS}
        total = sum(grouped.values())
        if total <= 0:
            return None
        scores = {k: v / total for k, v in grouped.items()}
        neutral = float(mean[self._label_index["_neutral"]].sum())
        return ReviewResult(
            review_id=review.id,
            author=review.author,
            text=text,
            scores=scores,
            dominant=max(scores, key=scores.get),
            neutral_share=neutral,
        )
