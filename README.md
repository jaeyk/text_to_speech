# PracticeTalk

This is a simple, lightweight local speech synthesis tool with a web interface that turns your talk script into an audio file, allowing you to check its flow and narrative.

Jae Yeon Kim and Codex (2026).

Use modes

- Recommended: run locally and use one URL only: `http://127.0.0.1:8000`
- Advanced: use GitHub Pages UI (`https://jaeyk.github.io/PracticeTalk/`) with a separate backend URL

Features

- Upload a `.txt` file or paste text and synthesize speech.
- Supports `en-US-AvaMultilingualNeural` (default) plus a few additional voices in the UI.
- Chunked synthesis for long texts and optional streaming (MP3) so large inputs don't time out.
- Adjustable `pace` (Slow, Normal, Fast, Faster) — pace adjusts speaking rate and sentence pause *length* (fixed base pause = 300ms).
- Slide markers like `Slide 1 Slide 2` are automatically skipped during synthesis.
- Output formats: `MP3` and `WAV`.
- Includes a `Dockerfile` and a GitHub Actions smoke test.

Quick start

1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. uvicorn main:app --reload --port 8000
4. Open <http://localhost:8000>

Local setup for non-technical users (Windows, Mac, Linux)

1. Download ZIP from `https://github.com/jaeyk/PracticeTalk` and unzip.
2. Install Python 3.12 from `https://www.python.org/downloads/`.
3. Open a terminal in the unzipped folder.
4. Run the commands for your operating system below.

Windows (Command Prompt)

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Mac (Terminal)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Linux (Terminal)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Then open:

- `http://127.0.0.1:8000`

Stop the app:

- Press `Ctrl + C` in the terminal.

Docker

- Build: docker build -t talk-practice .
- Run: docker run -p 8000:8000 talk-practice

GitHub Actions hosting

- The workflow `publish.yml` (push → main) deploys the `static/` site to **GitHub Pages** at `https://jaeyk.github.io/PracticeTalk/`.
- GitHub Pages is frontend-only. On that page, set **Backend URL** to your running FastAPI server (for example `https://<your-backend-host>`).
- If you do not have a backend URL, run locally and open `http://127.0.0.1:8000` instead.

Notes

- Streaming uses MP3 chunk streaming (MediaSource in the web UI).
- ETA & progress: the UI shows an estimated talk duration based on `pace` and text length and presents a playback progress bar while listening.
- Processing can be slow for long scripts or busy voice service periods. Please be patient after clicking **Synthesize**.
- Uploaded text must be UTF-8. Max input size ~200k characters (configurable in `main.py`).
