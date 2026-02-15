from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
import tempfile
import os
import re
import asyncio
import wave
import sys
import edge_tts
from typing import List
from pathlib import Path


def resolve_static_dir() -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base_dir = Path(__file__).resolve().parent
    return base_dir / "static"


STATIC_DIR = resolve_static_dir()
DIST_DIR = Path(__file__).resolve().parent / "dist"

app = FastAPI(title="Talk Practice — edge-tts")
# Development-friendly CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if DIST_DIR.exists():
    app.mount("/dist", StaticFiles(directory=str(DIST_DIR)), name="dist")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/help")
async def help_page():
    return FileResponse(str(STATIC_DIR / "help.html"))


@app.get("/help.html")
async def help_page_html():
    return FileResponse(str(STATIC_DIR / "help.html"))


@app.get("/app")
async def app_page():
    return FileResponse(str(STATIC_DIR / "app.html"))


@app.get("/app.html")
async def app_page_html():
    return FileResponse(str(STATIC_DIR / "app.html"))


# Small curated voice list for the UI
VOICES = [
    {"name": "Ava (en-US)", "value": "en-US-AvaMultilingualNeural"},
    {"name": "Jenny (en-US)", "value": "en-US-JennyNeural"},
    {"name": "Libby (en-GB)", "value": "en-GB-LibbyNeural"},
    {"name": "Natasha (en-AU)", "value": "en-AU-NatashaNeural"},
]


@app.get("/voices")
async def list_voices():
    return JSONResponse(content=VOICES)


@app.post("/estimate")
async def estimate(file: UploadFile | None = File(None), text: str | None = Form(None), pace: str | None = Form("normal")):
    """Return an estimated duration (seconds) for the provided text.

    Uses a fixed base sentence pause (300ms) which is scaled by `pace`.
    Response JSON includes: estimated_seconds, speech_seconds, pause_seconds,
    slide_pause_seconds, words, chars, sentences, slide_pauses, chunk_count.
    """
    if file is None and (text is None or not text.strip()):
        raise HTTPException(status_code=400, detail="No text provided")

    if file is not None:
        content = await file.read()
        try:
            text_to_est = content.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 text")
    else:
        text_to_est = (text or "").strip()

    if not text_to_est:
        raise HTTPException(status_code=400, detail="Text is empty")

    # preprocess slides
    preprocessed = preprocess_slides(text_to_est)

    words = len(re.findall(r"\w+", preprocessed))
    chars = len(preprocessed)
    sentences = len(SENTENCE_END_RE.findall(preprocessed))
    slide_pauses = preprocessed.count("__SLIDE_PAUSE__")

    # resolve pace -> pause multiplier
    prosody_rate, pause_multiplier = resolve_pace(pace or "normal")
    base_pause = DEFAULT_PAUSE_MS
    pause_seconds = (base_pause * pause_multiplier * sentences) / 1000.0
    slide_pause_seconds = slide_pauses * 3.0

    # approximate speaking time using words-per-minute per pace
    WPM = {"slow": 120, "normal": 160, "fast": 200, "faster": 240}
    wpm = WPM.get((pace or "normal").lower(), 160)
    speech_seconds = (words / max(1, wpm)) * 60.0

    estimated_seconds = speech_seconds + pause_seconds + slide_pause_seconds + 0.25
    chunk_count = len(split_text(preprocessed, max_chars=4000))

    return JSONResponse(content={
        "estimated_seconds": round(estimated_seconds, 2),
        "speech_seconds": round(speech_seconds, 2),
        "pause_seconds": round(pause_seconds, 2),
        "slide_pause_seconds": round(slide_pause_seconds, 2),
        "words": words,
        "chars": chars,
        "sentences": sentences,
        "slide_pauses": slide_pauses,
        "chunk_count": chunk_count,
    })


SENTENCE_END_RE = re.compile(r"(?<=[\.\?!])\s+")


# Pace configuration -> (SSML prosody rate, pause multiplier)
PACE_MAP = {
    "slow": ("-15%", 1.2),
    "normal": ("+0%", 1.0),
    "fast": ("+20%", 0.8),
    "faster": ("+40%", 0.6),
}

# default base pause (ms) inserted after sentence punctuation
DEFAULT_PAUSE_MS = 300

# match groups of Slide markers (e.g. "Slide 1 Slide 2 Slide 3")
SLIDE_RE = re.compile(r"(?:Slide\s*\d+\s*){1,}", flags=re.IGNORECASE)


def split_text(text: str, max_chars: int = 4000) -> List[str]:
    """Split text into chunks (prefer sentence boundaries)."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    parts: List[str] = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + max_chars, L)
        segment = text[start:end]
        matches = list(SENTENCE_END_RE.finditer(segment))
        if matches:
            split_at = matches[-1].end()
            parts.append(segment[:split_at].strip())
            start += split_at
        else:
            # fallback: hard split
            parts.append(segment.strip())
            start += len(segment)

        # skip whitespace between chunks
        while start < L and text[start].isspace():
            start += 1

    return parts


def preprocess_slides(text: str) -> str:
    """Replace consecutive slide markers with a slide-pause token."""
    return SLIDE_RE.sub("__SLIDE_PAUSE__", text)


def prepare_text_for_chunk(chunk: str) -> str:
    """Prepare plain text chunk for edge-tts (avoid raw SSML tags being spoken)."""
    return chunk.replace("__SLIDE_PAUSE__", " ")


def resolve_pace(pace: str):
    return PACE_MAP.get((pace or "").lower(), PACE_MAP["normal"])

@app.post("/synthesize")
async def synthesize(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    voice: str | None = Form("en-US-AvaMultilingualNeural"),
    fmt: str | None = Form("mp3"),
    pace: str | None = Form("normal"),
):
    """Synthesize text (file upload or pasted text).

    - `pace` controls speaking rate (slow | normal | fast | faster).
    - `Slide N` sequences are skipped during synthesis.
    """
    if file is None and (text is None or not text.strip()):
        raise HTTPException(status_code=400, detail="No text provided")

    if file is not None:
        content = await file.read()
        try:
            text_to_speak = content.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 text")
    else:
        text_to_speak = text or ""

    text_to_speak = text_to_speak.strip()
    if not text_to_speak:
        raise HTTPException(status_code=400, detail="Text is empty")

    if fmt not in ("mp3", "wav"):
        raise HTTPException(status_code=400, detail="Unsupported format")

    # validate inputs
    prosody_rate, _ = resolve_pace(pace or "normal")

    # preprocess slides (replace Slide markers with a token)
    text_to_speak = preprocess_slides(text_to_speak)

    MAX_CHARS = 200_000
    if len(text_to_speak) > MAX_CHARS:
        raise HTTPException(status_code=413, detail=f"Text too long (max {MAX_CHARS} characters)")

    # chunk size tuned for reliable synthesis
    CHUNK_SIZE = 4000
    chunks = split_text(text_to_speak, max_chars=CHUNK_SIZE)

    # --- MP3 path: synthesize per-chunk and append bytes ---
    if fmt == "mp3":
        fd, out_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            with open(out_path, "ab") as out_f:
                for chunk in chunks:
                    tmpfd, tmp_path = tempfile.mkstemp(suffix=".mp3")
                    os.close(tmpfd)
                    try:
                        text_chunk = prepare_text_for_chunk(chunk)
                        communicator = edge_tts.Communicate(text_chunk, voice=voice, rate=prosody_rate)
                        await communicator.save(tmp_path)
                        with open(tmp_path, "rb") as r:
                            out_f.write(r.read())
                    finally:
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
            return FileResponse(out_path, media_type="audio/mpeg", filename="speech.mp3", background=BackgroundTask(lambda: os.remove(out_path)))
        except Exception:
            try:
                os.remove(out_path)
            except Exception:
                pass
            raise

    # --- WAV path: merge WAV frames properly using wave module ---
    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    out_wav = None
    try:
        out_wav = wave.open(out_path, "wb")
        for i, chunk in enumerate(chunks):
            tmpfd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(tmpfd)
            try:
                text_chunk = prepare_text_for_chunk(chunk)
                communicator = edge_tts.Communicate(text_chunk, voice=voice, rate=prosody_rate)
                await communicator.save(tmp_path)
                with wave.open(tmp_path, "rb") as src:
                    if i == 0:
                        out_wav.setnchannels(src.getnchannels())
                        out_wav.setsampwidth(src.getsampwidth())
                        out_wav.setframerate(src.getframerate())
                    frames = src.readframes(src.getnframes())
                    out_wav.writeframes(frames)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        out_wav.close()
        out_wav = None
        return FileResponse(out_path, media_type="audio/wav", filename="speech.wav", background=BackgroundTask(lambda: os.remove(out_path)))
    finally:
        if out_wav is not None:
            out_wav.close()


@app.post("/synthesize_stream")
async def synthesize_stream(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    voice: str | None = Form("en-US-AvaMultilingualNeural"),
    pace: str | None = Form("normal"),
):
    """Stream MP3 bytes as chunks are synthesized.

    This endpoint streams `audio/mpeg` and is intended for clients that can
    progressively consume MP3 (the web UI uses MediaSource when streaming).
    """
    if file is None and (text is None or not text.strip()):
        raise HTTPException(status_code=400, detail="No text provided")

    if file is not None:
        content = await file.read()
        try:
            text_to_speak = content.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 text")
    else:
        text_to_speak = text or ""

    text_to_speak = text_to_speak.strip()
    if not text_to_speak:
        raise HTTPException(status_code=400, detail="Text is empty")

    # apply slide preprocessing and pace
    prosody_rate, _ = resolve_pace(pace or "normal")
    text_to_speak = preprocess_slides(text_to_speak)

    MAX_CHARS = 200_000
    if len(text_to_speak) > MAX_CHARS:
        raise HTTPException(status_code=413, detail=f"Text too long (max {MAX_CHARS} characters)")

    chunks = split_text(text_to_speak, max_chars=4000)

    async def generator():
        for chunk in chunks:
            tmpfd, tmp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(tmpfd)
            try:
                text_chunk = prepare_text_for_chunk(chunk)
                communicator = edge_tts.Communicate(text_chunk, voice=voice, rate=prosody_rate)
                await communicator.save(tmp_path)
                with open(tmp_path, "rb") as r:
                    while True:
                        data = r.read(16 * 1024)
                        if not data:
                            break
                        yield data
                        await asyncio.sleep(0)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    return StreamingResponse(generator(), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
