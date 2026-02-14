# PracticeTalk

This is a simple, lightweight, browser-based tool that turns your talk script into an audio file, allowing you to check its flow and narrative. Co-developed by Jae Yeon Kim and Codex.

Features
- Upload a `.txt` file or paste text and synthesize speech.
- Supports `en-US-AvaMultilingualNeural` (default) plus a few additional voices in the UI.
- Chunked synthesis for long texts and optional streaming (MP3) so large inputs don't time out.
- Adjustable `pace` (Slow, Normal, Fast, Faster) — pace adjusts speaking rate and sentence pause *length* (fixed base pause = 300ms).
- Slide markers like `Slide 1 Slide 2` are automatically skipped and replaced with a 3s pause.
- Output formats: `MP3` and `WAV`.
- Includes a `Dockerfile` and a GitHub Actions smoke test.

Quick start
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. uvicorn main:app --reload --port 8000
4. Open http://localhost:8000

Docker
- Build: docker build -t talk-practice .
- Run: docker run -p 8000:8000 talk-practice

GitHub Actions hosting
- The workflow `publish.yml` (push → main) deploys the `static/` site to **GitHub Pages** at `https://jaeyk.github.io/PracticeTalk/`.
- On GitHub Pages, set **Backend URL** in the UI to your running FastAPI server (for example `https://<your-backend-host>`). The `/estimate` and `/synthesize` endpoints are served by the backend, not by GitHub Pages.

Notes
- Streaming uses MP3 chunk streaming (MediaSource in the web UI).
- ETA & progress: the UI shows an estimated talk duration based on `pace` and text length and presents a playback progress bar while listening.
- Uploaded text must be UTF-8. Max input size ~200k characters (configurable in `main.py`).
