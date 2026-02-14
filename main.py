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
import edge_tts
from typing import List

app = FastAPI(title="Talk Practice — edge-tts")
# Development-friendly CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


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


SENTENCE_END_RE = re.compile(r"(?<=[\.\?!])\s+")


# Pace configuration -> (SSML prosody rate, pause multiplier)
PACE_MAP = {
    "slow": ("-15%", 1.2),
    "normal": ("0%", 1.0),
    "fast": ("+20%", 0.8),
    "faster": ("+40%", 0.6),
}

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


def escape_for_ssml(s: str) -> str:
    """Escape XML-special chars but preserve <break .../> tags."""
    breaks: List[str] = []

    def _store(m: re.Match) -> str:
        breaks.append(m.group(0))
        return f"__BREAK_{len(breaks)-1}__"

    # temporarily remove break tags
    s2 = re.sub(r"<break[^>]*?>", _store, s)
    # escape the rest
    s2 = s2.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # restore breaks
    for i, b in enumerate(breaks):
        s2 = s2.replace(f"__BREAK_{i}__", b)
    return s2


def insert_sentence_breaks(s: str, pause_ms: int) -> str:
    return SENTENCE_END_RE.sub(f"<break time=\"{pause_ms}ms\"/> ", s)


def prepare_ssml_for_chunk(chunk: str, pause_ms: int, prosody_rate: str) -> str:
    """Insert sentence breaks, replace slide-token with a 3s break, escape and wrap in SSML."""
    # add short breaks after sentence punctuation
    c = insert_sentence_breaks(chunk, pause_ms)
    # replace slide tokens with a fixed 3s pause
    c = c.replace("__SLIDE_PAUSE__", "<break time=\"3000ms\"/>")
    # escape while preserving break tags
    escaped = escape_for_ssml(c)
    # wrap in SSML; voice is still passed as Communicate(..., voice=...)
    ssml = f"<speak><prosody rate=\"{prosody_rate}\">{escaped}</prosody></speak>"
    return ssml


def resolve_pace(pace: str):
    return PACE_MAP.get((pace or "").lower(), PACE_MAP["normal"])

@app.post("/synthesize")
async def synthesize(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    voice: str | None = Form("en-US-AvaMultilingualNeural"),
    fmt: str | None = Form("mp3"),
    pace: str | None = Form("normal"),
    pause_ms: int | None = Form(300),
):
    """Synthesize text (file upload or pasted text).

    - `pace` controls speaking rate (slow | normal | fast | faster).
    - `pause_ms` sets the base sentence pause (multiplied by pace).
    - `Slide N` sequences are skipped and replaced with a 3s pause.
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
    prosody_rate, pause_multiplier = resolve_pace(pace or "normal")
    base_pause = max(0, int(pause_ms or 300))
    effective_pause = max(0, int(base_pause * pause_multiplier))

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
                        ssml = prepare_ssml_for_chunk(chunk, effective_pause, prosody_rate)
                        communicator = edge_tts.Communicate(ssml, voice=voice)
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
                ssml = prepare_ssml_for_chunk(chunk, effective_pause, prosody_rate)
                communicator = edge_tts.Communicate(ssml, voice=voice)
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
    pause_ms: int | None = Form(300),
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
    prosody_rate, pause_multiplier = resolve_pace(pace or "normal")
    base_pause = max(0, int(pause_ms or 300))
    effective_pause = max(0, int(base_pause * pause_multiplier))
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
                ssml = prepare_ssml_for_chunk(chunk, effective_pause, prosody_rate)
                communicator = edge_tts.Communicate(ssml, voice=voice)
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

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
