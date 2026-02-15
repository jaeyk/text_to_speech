#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d "dist/PracticeTalk.app" ]; then
  bash scripts/build_desktop.sh
fi

pkgbuild \
  --install-location "/Applications" \
  --component "dist/PracticeTalk.app" \
  "dist/PracticeTalk-mac.pkg"

echo "Installer build complete: dist/PracticeTalk-mac.pkg"
