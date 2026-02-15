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

The app is deployed on Hugging Face Spaces.

## Development (Optional)

Run locally with Docker:

```bash
docker run -p 7860:7860 jaeyk/talk-practice:latest
```

*(Note: Replace `jaeyk/talk-practice:latest` with your actual image name if different)*

Then open `http://127.0.0.1:7860` in your browser.

## Deployment

Deployment is automated via GitHub Actions to Hugging Face Spaces.

👉 [**See Deployment Guide**](DEPLOY.md)
