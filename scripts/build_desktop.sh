#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Error: Python 3.10+ is required."
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

VENV_PY=".venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt pyinstaller

rm -rf build dist

"$VENV_PY" -m PyInstaller \
  --noconfirm \
  --clean \
  --name PracticeTalk \
  --windowed \
  --add-data "static:static" \
  --collect-all edge_tts \
  desktop_launcher.py

echo "Build complete:"
echo "  macOS: dist/PracticeTalk.app"
echo "  Linux: dist/PracticeTalk"
