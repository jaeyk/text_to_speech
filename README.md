# text_to_speech

Small demo: browser-based talk-practice UI that uses `edge-tts` (Microsoft neural voices).

Features
- Upload a `.txt` file or paste text and synthesize speech.
- Supports `en-US-AvaMultilingualNeural` (default) plus a few additional voices in the UI.
- Chunked synthesis for long texts and optional streaming (MP3) so large inputs don't time out.
- Adjustable `pace` (Slow, Normal, Fast, Faster) and `pause` timer — pace adjusts speaking rate and sentence pauses.
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
- The workflow `publish.yml` (push → main) does two things:
  - Deploys the `static/` site to **GitHub Pages** (frontend only).
  - Builds and pushes a Docker image to **GitHub Container Registry (GHCR)** at `ghcr.io/<owner>/text_to_speech:latest`.

To run the backend container after GHCR publish:

```bash
docker run -p 8000:8000 ghcr.io/<your-org-or-username>/text_to_speech:latest
```

When the frontend is hosted on GitHub Pages, set the **Backend URL** field in the web UI to the public URL of your running backend (e.g. `https://example.com`), or host both UI and container behind the same domain and leave it blank.

Notes
- Streaming uses MP3 chunk streaming (MediaSource in the web UI).
- Uploaded text must be UTF-8. Max input size ~200k characters (configurable in `main.py`).
