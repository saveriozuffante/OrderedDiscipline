#!/usr/bin/env bash
set -euo pipefail

DEFAULT_URL=$(python - <<'PY'
import socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("1.1.1.1", 80))
        print(f"http://{sock.getsockname()[0]}:8000")
except OSError:
    print("http://127.0.0.1:8000")
PY
)

export UVICORN_WORKERS="${UVICORN_WORKERS:-1}"
export SHARE_URL="${SHARE_URL:-$DEFAULT_URL}"

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "$UVICORN_WORKERS"
