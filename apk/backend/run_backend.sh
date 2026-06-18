#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

python3 -m pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
