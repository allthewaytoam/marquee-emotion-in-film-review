import unittest
import warnings

from app import create_app
from app.config import Settings
from tests.fakes import SampleProvider


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = create_app(Settings.from_env(), provider=SampleProvider())
        cls.client = app.test_client()

    def test_health_reports_model_labels(self):
        body = self.client.get("/api/health").get_json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("neutral", body["labels"])

    def test_movie_list_and_search(self):
        everything = self.client.get("/api/movies").get_json()["movies"]
        self.assertGreaterEqual(len(everything), 4)
        found = self.client.get("/api/movies?query=lantern").get_json()["movies"]
        self.assertEqual([m["title"] for m in found], ["Paper Lanterns"])

    def test_analysis_contract(self):
        body = self.client.get("/api/movies/s3/analysis").get_json()
        self.assertEqual([e["key"] for e in body["emotions"]], ["joy", "sadness", "anger", "fear", "surprise"])
        self.assertAlmostEqual(sum(e["score"] for e in body["emotions"]), 1.0, places=2)
        self.assertEqual(body["final"]["key"], "joy")
        self.assertEqual(body["reviewsScored"], len(body["reviews"]))
        self.assertIn(body["emotions"][0]["strength"], {"strong", "moderate", "weak"})

    def test_unknown_movie_is_404_with_error_body(self):
        response = self.client.get("/api/movies/nope/analysis")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "movie_not_found")

    def test_frontend_is_served(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/js/main.js").status_code, 200)
        self.assertEqual(self.client.get("/css/tokens.css").status_code, 200)
