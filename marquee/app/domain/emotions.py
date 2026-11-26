"""Emotion taxonomy.

The classifier emits its own labels. The interface reports five major emotions.
This module is the single place that maps one to the other, so changing the
model's label set only means editing `LABEL_TO_MAJOR`.
"""
from __future__ import annotations

MAJOR_EMOTIONS: tuple[str, ...] = ("joy", "sadness", "anger", "fear", "surprise")

DISPLAY_NAMES: dict[str, str] = {
    "joy": "Joy",
    "sadness": "Sadness",
    "anger": "Anger",
    "fear": "Fear",
    "surprise": "Surprise",
}

# Model label -> major emotion. Finer labels can be folded in here.
LABEL_TO_MAJOR: dict[str, str] = {
    "joy": "joy",
    "sadness": "sadness",
    "anger": "anger",
    "fear": "fear",
    "surprise": "surprise",
}

# Labels that carry no emotion. Their mass is reported separately and removed
# before the five emotions are renormalised.
NON_EMOTION_LABELS: frozenset[str] = frozenset({"neutral"})

STRONG_THRESHOLD = 0.40
MODERATE_THRESHOLD = 0.22


def strength_of(share: float) -> str:
    """Bucket a share of the five-emotion total. A uniform split is 0.20."""
    if share >= STRONG_THRESHOLD:
        return "strong"
    if share >= MODERATE_THRESHOLD:
        return "moderate"
    return "weak"
