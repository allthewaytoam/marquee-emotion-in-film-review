"""Wrapper around the pickled TF-IDF vectoriser and LinearSVC model."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np

from app.errors import ModelLoadError

log = logging.getLogger(__name__)


class EmotionClassifier:
    """Turns text into a probability-like distribution over the model's labels.

    LinearSVC has no predict_proba, so margins from decision_function are passed
    through a temperature-scaled softmax. The values rank emotions and size them
    against each other; they are not calibrated probabilities.
    """

    def __init__(self, vectorizer, model, temperature: float = 2.0):
        self._vectorizer = vectorizer
        self._model = model
        self._temperature = temperature
        self._validate()

    @classmethod
    def from_paths(cls, vectorizer_path: Path, model_path: Path, temperature: float = 2.0):
        for path in (vectorizer_path, model_path):
            if not path.is_file():
                raise ModelLoadError(f"Model file not found: {path}")
        try:
            vectorizer = joblib.load(vectorizer_path)
            model = joblib.load(model_path)
        except Exception as exc:  # unpickling can fail in many ways
            raise ModelLoadError(f"Could not load model files: {exc}") from exc
        return cls(vectorizer, model, temperature)

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(str(label) for label in self._model.classes_)

    def predict_distribution(self, texts: Sequence[str]) -> np.ndarray:
        """Shape (len(texts), n_labels), rows sum to 1.

        A row is NaN when none of the text's words exist in the vocabulary: the
        model would then answer from its intercept alone, which is noise.
        """
        if not texts:
            return np.empty((0, len(self.labels)))
        matrix = self._vectorizer.transform(texts)
        margins = self._model.decision_function(matrix)
        if margins.ndim == 1:  # binary models return a vector
            margins = np.column_stack([-margins, margins])
        scaled = margins * self._temperature
        scaled -= scaled.max(axis=1, keepdims=True)
        weights = np.exp(scaled)
        probs = weights / weights.sum(axis=1, keepdims=True)
        probs[np.diff(matrix.indptr) == 0] = np.nan
        return probs

    def _validate(self) -> None:
        vocab_size = len(getattr(self._vectorizer, "vocabulary_", {}))
        expected = getattr(self._model, "n_features_in_", None)
        if expected is not None and expected != vocab_size:
            raise ModelLoadError(
                f"Vectoriser and model do not belong together: vectoriser has "
                f"{vocab_size} features, model expects {expected}."
            )
        if not hasattr(self._model, "decision_function"):
            raise ModelLoadError("Model has no decision_function; expected a linear classifier.")
        log.info("Emotion model ready: labels=%s, features=%d", self.labels, vocab_size)
