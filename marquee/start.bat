@echo off
rem One-command launcher for Windows.
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Install it from python.org and tick "Add Python to PATH".
  pause
  exit /b 1
)

if not exist .env if exist .env.example copy .env.example .env >nul

findstr /r /c:"^TMDB_API_KEY=." /c:"^TMDB_ACCESS_TOKEN=." .env >nul 2>&1
if errorlevel 1 (
  set /p KEY=Paste your TMDB API key ^(free: themoviedb.org/settings/api^): 
  > .env echo TMDB_API_KEY=%KEY%
)

if not exist .venv python -m venv .venv
call .venv\Scripts\activate
echo Installing requirements. The first run can take a minute or two...
pip install -q -r requirements.txt
if errorlevel 1 (
  echo Install failed. Check your internet connection and try again.
  pause
  exit /b 1
)

echo.
echo Starting at http://127.0.0.1:5000  (close this window to stop)
start "" http://127.0.0.1:5000
python run.py
pause
