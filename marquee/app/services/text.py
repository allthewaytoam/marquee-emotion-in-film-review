"""Review text preparation.

The vectoriser lower-cases and tokenises on its own, so cleaning here is limited
to markup and links that review sources add.
"""
from __future__ import annotations

import html
import re

_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_URL = re.compile(r"https?://\S+|www\.\S+")
_MD_MARKS = re.compile(r"[*`#>~]+|(?<!\w)_+|_+(?!\w)")
_WHITESPACE = re.compile(r"\s+")
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


def clean_review(raw: str) -> str:
    text = html.unescape(raw or "")
    text = _MD_LINK.sub(r"\1", text)
    text = _URL.sub(" ", text)
    text = _MD_MARKS.sub(" ", text)
    return _WHITESPACE.sub(" ", text).strip()


def split_into_chunks(text: str, min_words: int = 4, max_chunks: int = 60) -> list[str]:
    """Sentence-level chunks. Long reviews dilute TF-IDF vectors, so each
    sentence is scored on its own and the results are averaged afterwards."""
    chunks = [s for s in _SENTENCE_BREAK.split(text) if len(s.split()) >= min_words]
    if not chunks and text:
        chunks = [text]
    return chunks[:max_chunks]
