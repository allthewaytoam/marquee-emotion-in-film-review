# Marquee

Emotion detection for movie reviews. Pick a film, the backend fetches its reviews,
scores them with the TF-IDF + LinearSVC model, and the interface shows how strongly
each of five major emotions came through and which one wins overall.

## Run

Windows: double-click `start.bat`. macOS/Linux: `./start.sh`. It sets up the environment,
asks for your TMDB key once, and starts the app at http://127.0.0.1:5000.

Manual setup:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then paste your TMDB key into .env
python run.py                   # http://127.0.0.1:5000
```

Reviews come live from TMDB, so a free key is required (https://www.themoviedb.org/settings/api).
The app refuses to start without one and says so.

## Verify

```bash
python -m unittest discover -s tests -t .
python -m scripts.check_pipeline
```

## Layout

```
app/
  api/            routes and JSON serializers
  domain/         entities and the emotion taxonomy (label mapping lives here)
  providers/      review sources (tmdb.py)
  services/       classifier wrapper, analysis, film orchestration, cache
web/              static frontend (ES modules, no build step)
models/           the two pickles
tests/  scripts/   (tests/fakes.py holds invented films, used only by tests)
```

## How scoring works

1. Each review is cleaned (markup, links) and split into sentences. TF-IDF vectors of
   long texts get diluted, so sentences are scored separately and averaged per review.
2. LinearSVC has no probabilities. Margins go through a temperature-scaled softmax
   (`SCORE_TEMPERATURE`). Treat the output as relative strength, not calibrated probability.
3. The model's `neutral` class is removed and the remaining five are renormalised to 100%.
   The neutral share is reported separately.
4. The film score is the mean of per-review scores. The final prediction is the highest.

## Things to confirm with the team

- **Preprocessing at training time.** The vectoriser lowercases and tokenises itself, but if
  training used extra cleaning (stop words, lemmatising, emoji handling), replicate it in
  `app/services/text.py`, or scores will drift.
- **scikit-learn version.** The pickles were saved with 1.6.1; `requirements.txt` pins it.
- **Label set.** The model emits six labels. Mapping to five major emotions is in
  `app/domain/emotions.py`; edit `LABEL_TO_MAJOR` if the label set changes.
