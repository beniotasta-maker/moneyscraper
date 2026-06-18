#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "[build] Installing Python build tools if needed..."
python3 -m pip install --upgrade pip buildozer cython

echo "[build] Starting Buildozer Android debug build..."
buildozer -v android debug

echo "[build] APK output is usually in $ROOT_DIR/bin/"
