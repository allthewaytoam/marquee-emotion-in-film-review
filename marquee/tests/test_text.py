import unittest

from app.services.text import clean_review, split_into_chunks


class CleanReviewTests(unittest.TestCase):
    def test_strips_markdown_links_and_urls(self):
        raw = "Loved it. See [my blog](https://x.io/a) or https://spam.example now."
        self.assertEqual(clean_review(raw), "Loved it. See my blog or now.")

    def test_unescapes_entities_and_collapses_whitespace(self):
        self.assertEqual(clean_review("Tom &amp; Jerry\r\n\r\n  rule"), "Tom & Jerry rule")

    def test_empty_input(self):
        self.assertEqual(clean_review(""), "")


class SplitTests(unittest.TestCase):
    def test_drops_very_short_sentences(self):
        text = "Great. The acting was truly wonderful in every scene."
        self.assertEqual(split_into_chunks(text), ["The acting was truly wonderful in every scene."])

    def test_short_review_falls_back_to_whole_text(self):
        self.assertEqual(split_into_chunks("Superb film"), ["Superb film"])

    def test_caps_chunk_count(self):
        text = " ".join(["This is a perfectly fine sentence."] * 100)
        self.assertEqual(len(split_into_chunks(text, max_chunks=10)), 10)
