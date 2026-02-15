# PracticeTalk

PracticeTalk turns your script into audio so you can rehearse your talk in a browser.

Jae Yeon Kim and Codex (2026).

## Start Here (No Terminal Needed)

### Mac

1. Double-click `run_local.command`.
2. Your browser opens to `http://127.0.0.1:8000`.
3. Paste text or upload `.txt`, then click synthesize.

If macOS warns about security, right-click `run_local.command` and choose `Open`.

### Windows

1. Double-click `run_local.bat`.
2. Your browser opens to `http://127.0.0.1:8000`.
3. Paste text or upload `.txt`, then click synthesize.

Keep the launcher window open while using PracticeTalk. Close it to stop the app.

In-app help website:

- `http://127.0.0.1:8000/help`

## First-Time Setup (Automatic)

The launcher does this for you:

1. Finds Python 3.10+
2. Creates `.venv` if needed
3. Installs dependencies from `requirements.txt`
4. Starts the server on `127.0.0.1:8000`
5. Opens your browser

## Troubleshooting

- Python missing: install from `https://www.python.org/downloads/`, then run the launcher again.
- Browser did not open: manually go to `http://127.0.0.1:8000`.
- Port `8000` in use: close the other app using port 8000, then restart launcher.

## Advanced (Terminal)

Mac/Linux:

```bash
bash scripts/run_local.sh
```

Windows:

```bat
scripts\run_local.bat
```

Manual server start:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

## Features

- Paste text or upload `.txt`
- Voices including `en-US-AvaMultilingualNeural`
- MP3 and WAV output
- Speed control (`pace`)
- Long-text chunked synthesis
- Slide markers like `Slide 1` are skipped automatically

## Docker

- `docker build -t talk-practice .`
- `docker run -p 8000:8000 talk-practice`

## Desktop App Build (Downloadable Bundle)

You can package PracticeTalk as a desktop app so users can just open it.

macOS / Linux:

```bash
bash scripts/build_desktop.sh
```

Windows:

```bat
scripts\build_desktop.bat
```

Build outputs:

- macOS: `dist/PracticeTalk.app`
- Windows: `dist/PracticeTalk.exe`

Share that built file with users on the same OS. When they open it, it starts PracticeTalk and opens the app in a browser.

## Installer Build (Recommended for End Users)

These produce normal installer files (install wizard / installer package):

macOS:

```bash
bash scripts/build_installer_macos.sh
```

Windows:

```bat
scripts\build_installer_windows.bat
```

Installer outputs:

- macOS installer: `dist/PracticeTalk-mac.pkg`
- Windows installer: `dist/PracticeTalk-Setup.exe`

After install, users can launch PracticeTalk from Applications (macOS) or Start Menu/Desktop shortcut (Windows).

## Auto Release (GitHub)

When you push a version tag (example: `v1.0.0`), GitHub Actions will:

1. Build macOS and Windows installers
2. Create a GitHub Release for that tag
3. Attach downloadable files

Release files:

- `PracticeTalk-mac.pkg`
- `PracticeTalk-mac.zip`
- `PracticeTalk-Setup.exe`
- `PracticeTalk.exe`

Tag and push example:

```bash
git tag v1.0.0
git push origin v1.0.0
```
