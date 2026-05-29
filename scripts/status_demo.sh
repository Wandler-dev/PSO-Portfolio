#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT="${BACKEND_PORT:-${PSO_API_PORT:-8000}}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

pid_status() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "$name: stopped (no pid file)"
    return 1
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -n "$pid" && "$(ps -p "$pid" -o pid= 2>/dev/null | tr -d ' ')" == "$pid" ]]; then
    echo "$name: running (pid $pid)"
    return 0
  fi

  echo "$name: stopped (stale pid ${pid:-unknown})"
  return 1
}

check_url() {
  local name="$1"
  local url="$2"
  python - "$url" <<'PY'
import json
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=2) as response:
        body = response.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
            print(json.dumps(payload, ensure_ascii=False)[:300])
        except json.JSONDecodeError:
            print(f"HTTP {response.status}")
except Exception as exc:
    print(f"unreachable: {exc}")
    sys.exit(1)
PY
}

pid_status "backend" ".run/backend.pid" || true
pid_status "frontend" ".run/frontend.pid" || true

echo -n "backend health response summary: "
check_url "backend" "http://127.0.0.1:${BACKEND_PORT}/api/health" || true

echo -n "frontend URL: http://127.0.0.1:${FRONTEND_PORT} - "
check_url "frontend" "http://127.0.0.1:${FRONTEND_PORT}" || true
