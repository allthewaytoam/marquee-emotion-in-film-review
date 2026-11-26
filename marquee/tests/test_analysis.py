import unittest

import numpy as np

from app.domain.entities import Review
from app.errors import ModelLoadError
from app.services.analysis import EmotionAnalyzer

LABELS = ("anger", "fear", "joy", "neutral", "sadness", "surprise")


class StubModel:
    """Returns a fixed distribution per keyword found in the text."""

    labels = LABELS
    table = {
        "joy": [0.0, 0.0, 0.8, 0.2, 0.0, 0.0],
        "fear": [0.0, 0.7, 0.0, 0.3, 0.0, 0.0],
        "flat": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    }

    def predict_distribution(self, texts):
        rows = []
        for text in texts:
            hit = next((k for k in self.table if k in text), None)
            rows.append(self.table[hit] if hit else [np.nan] * len(LABELS))
        return np.array(rows, dtype=float)


def review(i, text):
    return Review(str(i), f"user{i}", text)


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = EmotionAnalyzer(StubModel())

    def test_neutral_is_removed_before_renormalising(self):
        result = self.analyzer.analyze([review(1, "pure joy in every single frame")])
        self.assertAlmostEqual(result.reviews[0].scores["joy"], 1.0)
        self.assertAlmostEqual(result.reviews[0].neutral_share, 0.2)

    def test_scores_sum_to_one(self):
        result = self.analyzer.analyze([review(1, "joy is here today friends")])
        self.assertAlmostEqual(sum(e.score for e in result.emotions), 1.0)

    def test_final_is_highest_mean_and_counts_leaders(self):
        reviews = [
            review(1, "joy fills this whole film"),
            review(2, "joy again and again here"),
            review(3, "fear grips this whole film"),
        ]
        result = self.analyzer.analyze(reviews)
        self.assertEqual(result.final, "joy")
        led = {e.key: e.led_reviews for e in result.emotions}
        self.assertEqual((led["joy"], led["fear"]), (2, 1))

    def test_unscorable_reviews_are_skipped(self):
        result = self.analyzer.analyze([review(1, "joy joy joy joy"), review(2, "qqq www eee rrr")])
        self.assertEqual(len(result.reviews), 1)
        self.assertEqual(result.skipped_reviews, 1)

    def test_all_unscorable_gives_empty_analysis(self):
        result = self.analyzer.analyze([review(1, "qqq www eee rrr")])
        self.assertEqual(result.reviews, [])
        self.assertEqual(result.final, "")

    def test_flat_only_review_is_skipped_not_divided_by_zero(self):
        result = self.analyzer.analyze([review(1, "flat flat flat flat")])
        self.assertEqual(result.reviews, [])

    def test_unmapped_label_fails_loudly(self):
        class Odd(StubModel):
            labels = ("joy", "love")

        with self.assertRaises(ModelLoadError):
            EmotionAnalyzer(Odd())
