---
title: PracticeTalk
emoji: "🎙️"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# PracticeTalk

PracticeTalk turns your script into audio so you can rehearse your talk in a browser.

Jae Yeon Kim and Codex (2026).

## Recent Updates

- Added desktop launcher app entrypoint: `desktop_launcher.py`
- Added installer build scripts:
  - `scripts/build_installer_macos.sh`
  - `scripts/build_installer_windows.bat`
- Added Windows installer spec: `installers/windows/practicetalk.iss`
- Added user help page: `static/help.html` (served at `/help`)
- Added CI workflows:
  - Manual desktop artifact build: `.github/workflows/desktop-build.yml`
  - Tag-based release publishing: `.github/workflows/release.yml`

## Quick Start (Docker)

No installation required. Just run:

```bash
docker run -p 7860:7860 jaeyk/talk-practice:latest
```

*(Note: Replace `jaeyk/talk-practice:latest` with your actual image name if different)*

Then open `http://127.0.0.1:7860` in your browser.

## Cloud Deployment (Free)

You can run this app without any local setup by deploying to **Hugging Face Spaces**.

👉 [**See Deployment Guide**](DEPLOY.md)

## Manual Install (Optional)

If you prefer to run without Docker:

### Mac

1. Download `run_local.command` (or the source code).
2. Double-click `run_local.command`.

### Windows

1. Download `run_local.bat` (or the source code).
2. Double-click `run_local.bat`.

## Advanced

... (rest of the sections regarding development or building from source)
