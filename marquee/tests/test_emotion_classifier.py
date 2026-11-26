import unittest
import warnings

import numpy as np

from app.config import Settings
from app.errors import ModelLoadError
from app.services.emotion_classifier import EmotionClassifier

SETTINGS = Settings.from_env()
HAVE_MODELS = SETTINGS.model_path.is_file() and SETTINGS.vectorizer_path.is_file()


@unittest.skipUnless(HAVE_MODELS, "model files not present")
class RealModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cls.clf = EmotionClassifier.from_paths(SETTINGS.vectorizer_path, SETTINGS.model_path)

    def test_labels(self):
        self.assertEqual(self.clf.labels, ("anger", "fear", "joy", "neutral", "sadness", "surprise"))

    def test_rows_are_distributions(self):
        probs = self.clf.predict_distribution(["I loved this film", "A truly terrifying night"])
        self.assertEqual(probs.shape, (2, 6))
        np.testing.assert_allclose(probs.sum(axis=1), 1.0)

    def test_out_of_vocabulary_text_is_nan(self):
        probs = self.clf.predict_distribution(["xkqzvw plmqrz"])
        self.assertTrue(np.isnan(probs).all())

    def test_clear_cases(self):
        cases = {
            "joy": "What a beautiful, joyful film, I smiled from start to finish and loved every minute",
            "fear": "I was terrified the whole time, my heart was racing and I could not look at the screen",
            "anger": "This movie made me so angry, the script is insulting and the director should be ashamed",
            "sadness": "I cried at the ending, such a heartbreaking and lonely story about loss",
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected):
                row = self.clf.predict_distribution([text])[0]
                self.assertEqual(self.clf.labels[int(np.argmax(row))], expected)


class LoadErrorTests(unittest.TestCase):
    def test_missing_file(self):
        from pathlib import Path

        with self.assertRaises(ModelLoadError):
            EmotionClassifier.from_paths(Path("/nope/a.pkl"), Path("/nope/b.pkl"))

    def test_mismatched_artefacts_are_rejected(self):
        class Vec:
            vocabulary_ = {"a": 0, "b": 1}

        class Model:
            n_features_in_ = 5
            classes_ = ["joy"]

            def decision_function(self, X):
                return X

        with self.assertRaises(ModelLoadError):
            EmotionClassifier(Vec(), Model())
