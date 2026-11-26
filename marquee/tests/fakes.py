"""Test double: invented films and reviews. Never used by the running app.

Lets the whole stack run without network access or API credentials. Nothing here
describes a real film.
"""
from __future__ import annotations

from app.domain.entities import Movie, Review
from app.errors import MovieNotFound

_FILMS: dict[str, tuple[Movie, list[tuple[str, str]]]] = {
    "s1": (
        Movie("s1", "The Salt Harbour", "2023", "A widowed ferry pilot takes one last crossing through a storm.", None),
        [
            ("harlow", "I cried through the entire last act. The loneliness of the pilot after losing his wife is handled so gently. A heartbreaking, sorrowful film."),
            ("mina_k", "The storm sequences terrified me. I gripped the armrest for twenty minutes and could barely breathe. Frightening in the best way."),
            ("dtran", "Beautiful and moving. The final crossing left me teary and grateful. I miss the characters already."),
            ("oakes", "Slow, and a little dull in the middle, but the ending is devastating and sad."),
            ("pell", "I loved the warm scenes at the harbour cafe. They made me smile and feel hopeful."),
        ],
    ),
    "s2": (
        Movie("s2", "Nine Floors Down", "2022", "A night-shift technician discovers a lift that stops at a floor that does not exist.", None),
        [
            ("r_vance", "Absolutely terrifying. I was afraid to look at the screen and the dread never lets up. I was scared stiff."),
            ("ines", "The scream in the stairwell made me jump out of my seat. Panic and fear from start to finish."),
            ("bowman", "Nobody could have predicted that ending. I was shocked and stunned, my jaw dropped."),
            ("sol", "Creepy and tense, but the script is lazy and the characters make furious, stupid choices that made me angry."),
            ("quill", "A frightening and eerie film. I was nervous the whole time."),
        ],
    ),
    "s3": (
        Movie("s3", "Paper Lanterns", "2024", "Three siblings reunite to open their late grandmother's lantern shop for one festival night.", None),
        [
            ("junoh", "Pure joy. I laughed out loud, smiled constantly and left the cinema happy and delighted."),
            ("amelie_b", "Such a warm, lovely film. I adored every minute and felt wonderfully cheerful afterwards."),
            ("teo", "What a wonderful surprise. I did not expect to enjoy it this much, and the twist at the lantern release amazed me."),
            ("harp", "Sweet and funny. The family scenes made me grin. I loved it."),
            ("wynn", "A bit sentimental, but I was delighted by the music and the colours. Happy and thrilled."),
        ],
    ),
    "s4": (
        Movie("s4", "A Fair Account", "2021", "An auditor uncovers a fraud that reaches her own family.", None),
        [
            ("greaves", "I was furious watching this. The betrayal is infuriating and the villain's smugness made me so angry."),
            ("nadia", "Outrageous and enraging. I hated how the company got away with everything. Disgusted and angry."),
            ("kell", "Cold and bitter, but gripping. The injustice made my blood boil."),
            ("sevan", "The confrontation scene left me stunned. I never saw it coming and gasped out loud."),
            ("omar_l", "Sad ending. I felt hopeless and heartbroken for the daughter."),
        ],
    ),
}


class SampleProvider:
    name = "sample"

    def list_movies(self, query: str = "", page: int = 1) -> list[Movie]:
        if page > 1:
            return []
        query = query.strip().lower()
        movies = [movie for movie, _ in _FILMS.values()]
        return [m for m in movies if query in m.title.lower()] if query else movies

    def get_movie(self, movie_id: str) -> Movie:
        try:
            return _FILMS[movie_id][0]
        except KeyError:
            raise MovieNotFound("No sample film with that id.") from None

    def get_reviews(self, movie_id: str, limit: int) -> list[Review]:
        if movie_id not in _FILMS:
            raise MovieNotFound("No sample film with that id.")
        rows = _FILMS[movie_id][1][:limit]
        return [Review(f"{movie_id}-{i}", author, text) for i, (author, text) in enumerate(rows, 1)]
