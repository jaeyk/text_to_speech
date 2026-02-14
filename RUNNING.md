Run locally

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

3. Open in your browser: http://localhost:8000

Docker

```bash
docker build -t talk-practice .
docker run -p 8000:8000 talk-practice
```

Endpoints
- `POST /synthesize` — accepts `file` (text) OR `text` (form field). Optional form fields: `voice`, `fmt` (`mp3` or `wav`). Returns the audio file.
- `POST /synthesize_stream` — streams `audio/mpeg` (MP3) in chunks as they are generated.

Notes
- Streaming is MP3-only in the demo and uses MediaSource in the web UI.
- Max input ~200k characters. Adjust `CHUNK_SIZE` / `MAX_CHARS` in `main.py` as needed.
