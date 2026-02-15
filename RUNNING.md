Run locally (no terminal)

- Mac: double-click `run_local.command`
- Windows: double-click `run_local.bat`
- App URL: `http://127.0.0.1:8000`

The launcher handles environment setup and dependency install automatically.

Run locally (terminal)

```bash
bash scripts/run_local.sh
```

or

```bat
scripts\run_local.bat
```

Docker

```bash
docker build -t talk-practice .
docker run -p 8000:8000 talk-practice
```

Desktop app bundle (for sharing)

- macOS/Linux build: `bash scripts/build_desktop.sh`
- Windows build: `scripts\build_desktop.bat`
- Output files: `dist/PracticeTalk.app` (macOS), `dist/PracticeTalk.exe` (Windows)

Installer package (recommended for non-technical users)

- macOS installer build: `bash scripts/build_installer_macos.sh`
- Windows installer build: `scripts\build_installer_windows.bat`
- Output files: `dist/PracticeTalk-mac.pkg` (macOS), `dist/PracticeTalk-Setup.exe` (Windows)

Endpoints
- `POST /synthesize` — accepts `file` (text) OR `text` (form field). Optional form fields: `voice`, `fmt` (`mp3` or `wav`). Returns the audio file.
- `POST /synthesize_stream` — streams `audio/mpeg` (MP3) in chunks as they are generated.

Notes
- Streaming is MP3-only in the demo and uses MediaSource in the web UI.
- Max input ~200k characters. Adjust `CHUNK_SIZE` / `MAX_CHARS` in `main.py` as needed.
