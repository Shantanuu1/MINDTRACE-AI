# MINDTRACE AI: Echoes of the Last Train

*Every lie leaves a trace. Every choice changes the truth.*

A browser detective game (Flask + vanilla JS). Suspects are voiced by a **local open-weight model, Gemma, via Ollama** (`gemma4:e2b`), while a deterministic Python engine owns the canonical mystery, evidence rules, Truth Tracker, scoring and endings. The model never decides the culprit.

## Features
Landing, Case Files, Investigation Hub (5 locations, 7 clues), Suspect Dossiers, Interrogation Room, Evidence Board (confirmed / plausible / unsupported connections), Detective Journal (timeline, transcripts, notes, search), Accusation Room (3 endings), Resolution, Profile, Settings. Difficulty (easy/normal/hard) changes hints, suggested questions, clue detail, AI tone and score multiplier. Progress is saved to `data/save.json`.

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama list        # confirm gemma4:e2b is listed (do NOT download another model)
python app.py
```
Open the address Flask prints (usually http://127.0.0.1:5000).

## Configuration
Copy `.env.example` to `.env` (optional). Defaults: `OLLAMA_URL=http://127.0.0.1:11434`, `OLLAMA_MODEL=gemma4:e2b`, `OLLAMA_TIMEOUT=90`. (`.env` loading needs `python-dotenv`; otherwise set environment variables in PowerShell, e.g. `$env:OLLAMA_MODEL="gemma4:e2b"`.)

## How to play
Explore locations, interview suspects (type or use suggested questions), watch the Truth Tracker in the Journal, connect clues, then accuse with suspect, motive, evidence and timeline.

## AI fallback
If Ollama is down, the model is missing, or a reply times out/is malformed, the game uses predefined dialogue clearly labelled "Predefined fallback dialogue". There is a Retry button; requests are not retried automatically.

## Tests
`python -m pytest -q` (Ollama is mocked; temp save files are used).

## Privacy and limits
Interrogation text is sent only to your local Ollama service; there are no external calls or trackers. This is a hobby project, not a security guarantee. One case, three suspects; the AI is not fine-tuned; the Truth Tracker uses deterministic rules (no AI classification); the Evidence Board has no drawn connection lines; no audio assets are included; the app was not verified against a live gemma4:e2b in the build environment.

## Structure
`app.py` routes · `story_data.py` public story · `canon.py` canonical solution · `game_engine.py` rules · `scoring.py` · `ai_service.py` · `storage.py` · `templates/` · `static/` · `tests/`

MIT License.
