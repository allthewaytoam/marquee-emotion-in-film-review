#!/usr/bin/env sh
# One-command launcher for macOS and Linux.
set -e
cd "$(dirname "$0")"

[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

[ -f .env ] || { [ -f .env.example ] && cp .env.example .env; }

if ! grep -qE '^TMDB_(API_KEY|ACCESS_TOKEN)=.+' .env 2>/dev/null; then
  printf "Paste your TMDB API key (free: themoviedb.org/settings/api): "
  read -r key
  printf "TMDB_API_KEY=%s\n" "$key" > .env
fi

echo "Open http://127.0.0.1:5000"
python run.py
