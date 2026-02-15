# Deployment Guide (Hugging Face Spaces)

If you don't want to run the app locally, you can deploy it for free on Hugging Face Spaces using Docker.

## Steps

1. **Create a Space**:
    - Go to [huggingface.co/spaces](https://huggingface.co/spaces).
    - Click **Create new Space**.
    - **Name**: `practice-talk` (or similar).
    - **SDK**: Select **Docker**.
    - **Space Hardware**: **Free (CPU basic)** is sufficient.
    - **Visibility**: Public or Private.

### Option 1: Automatic Sync (Recommended)

1. **Get your Token**:
    - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
    - Create a **Write** token (e.g., `GITHUB_ACTION`).
2. **Add Secret to GitHub**:
    - Go to your GitHub repo -> **Settings** -> **Secrets and variables** -> **Actions**.
    - Click **New repository secret**.
    - **Name**: `HF_TOKEN`
    - **Value**: (Paste your token)
3. **Update Config**:
    - Edit `.github/workflows/deploy-space.yml` in this repo.
    - Change `jaeyk/practice-talk` to your actual Space name (e.g., `your-username/space-name`).
4. **Push**:
    - Once you push this code to GitHub, the Action will run and deploy your app to Spaces automatically!

### Option 2: Manual Uploadfs

1. **Upload Files**:
    - Upload the contents of this repository to your Space.
    - specifically, ensure `Dockerfile`, `requirements.txt`, `main.py`, and the `static/` folder are uploaded.

2. **Port Configuration**:
    - This repository is configured to listen on **port 7860**, which is the default for Hugging Face Spaces.
    - The `Dockerfile` exposes this port automatically.

3. **Access the App**:
    - Once built (approx. 2-5 mins), your app will be live at `https://huggingface.co/spaces/<your-username>/<space-name>`.
