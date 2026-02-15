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

## Live App

PracticeTalk is live on Hugging Face Spaces (Docker SDK).

- Main app route: `/`
- App route: `/app`
- Help route: `/help`

## What Changed

- Hugging Face Spaces deployment is configured and working.
- GitHub Actions deploys a clean snapshot to Spaces (excludes `dist/`, `build/`, `.venv/`).
- README includes required Hugging Face front matter for Space config.
- UI is cleaned up for hosted usage:
  - Removed "New here?" local-install guide links from the app UI.
  - Removed embedded "How to run locally" blocks in hosted pages.
  - Backend URL now defaults to same-origin for hosted environments.

## Deployment Automation

- Workflow: `.github/workflows/deploy-space.yml`
- Trigger: push to `main` (and manual `workflow_dispatch`)
- Required GitHub secret: `HF_TOKEN`
- Recommended GitHub variable: `HF_SPACE_REPO` (`<username>/<space-name>`)

Full setup instructions: [DEPLOY.md](DEPLOY.md)

## Local Development (Optional)

Run locally with Docker:

```bash
docker run -p 7860:7860 jaeyk/talk-practice:latest
```

*(Note: Replace `jaeyk/talk-practice:latest` with your actual image name if different)*

Then open `http://127.0.0.1:7860` in your browser.

## API Endpoints

- `GET /voices`
- `POST /estimate`
- `POST /synthesize`
- `POST /synthesize_stream`
