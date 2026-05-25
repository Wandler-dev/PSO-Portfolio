#!/usr/bin/env bash
set -euo pipefail

ROOT_HINT="Please run this script from the project root: bash scripts/start_demo.sh"

if [[ ! -f "backend/app/main.py" || ! -f "frontend/package.json" ]]; then
  echo "$ROOT_HINT"
  exit 1
fi

RUN_DIR="$(pwd)/.run"
mkdir -p "$RUN_DIR"
STARTED_PID_FILES=()

port_in_use() {
  local port="$1"
  python - "$port" <<'PY'
import socket
import sys

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex(("127.0.0.1", int(sys.argv[1])))
    sock.close()
    sys.exit(0 if result == 0 else 1)
except OSError:
    sys.exit(1)
PY
}

wait_for_url() {
  local url="$1"
  local name="$2"
  local attempts=30
  local index=1
  while [[ "$index" -le "$attempts" ]]; do
    if python - "$url" <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=1) as response:
        if response.status < 500:
            sys.exit(0)
except Exception:
    pass
sys.exit(1)
PY
    then
      echo "$name is reachable: $url"
      return 0
    fi
    sleep 1
    index=$((index + 1))
  done
  echo "Warning: $name was not reachable within ${attempts}s: $url"
  return 1
}

url_reachable() {
  local url="$1"
  python - "$url" <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=1) as response:
        sys.exit(0 if response.status < 500 else 1)
except Exception:
    sys.exit(1)
PY
}

print_access_urls() {
  echo "Frontend URL: http://127.0.0.1:5173"

  local wsl_ip
  wsl_ip="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
  if [[ -n "${wsl_ip}" ]]; then
    echo "WSL IP frontend URL: http://${wsl_ip}:5173"
  fi
}

stop_started_processes() {
  for pid_file in "${STARTED_PID_FILES[@]}"; do
    if [[ -f "$pid_file" ]]; then
      local pid
      pid="$(cat "$pid_file")"
      if [[ -n "$pid" ]] && ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid" || true
      fi
      rm -f "$pid_file"
    fi
  done
}

echo "Checking backend Python dependencies..."
python - <<'PY'
import fastapi
import numpy
import pandas
import uvicorn

print("backend dependencies: ok")
PY

if [[ ! -f "frontend/package.json" ]]; then
  echo "frontend/package.json was not found."
  exit 1
fi

backend_already_running=0
frontend_already_running=0

if port_in_use 8000; then
  if url_reachable "http://127.0.0.1:8000/api/health"; then
    backend_already_running=1
    echo "Backend already running on port 8000."
  else
    echo "Port 8000 is already in use, but it does not look like this project's FastAPI service."
    echo "Run scripts/stop_demo.sh if it is a previous Demo process, or handle the process manually."
    exit 1
  fi
fi

if port_in_use 5173; then
  if url_reachable "http://127.0.0.1:5173"; then
    frontend_already_running=1
    echo "Frontend already running on port 5173."
  else
    echo "Port 5173 is already in use, but it does not look like this project's Vite frontend."
    echo "Run scripts/stop_demo.sh if it is a previous Demo process, or handle the process manually."
    exit 1
  fi
fi

if [[ "$backend_already_running" -eq 1 && "$frontend_already_running" -eq 1 ]]; then
  echo "Demo is already running. Closing the browser does not stop the backend/frontend services."
  print_access_urls
  echo "Use scripts/stop_demo.sh or make stop when you want to stop the services."
  exit 0
fi

if [[ ! -d "frontend/node_modules" ]]; then
  echo "frontend/node_modules not found; running npm install..."
  (cd frontend && npm install)
fi

if [[ "$backend_already_running" -eq 0 ]]; then
  echo "Starting FastAPI backend..."
  if command -v setsid > /dev/null 2>&1; then
    nohup setsid python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > "$RUN_DIR/backend.log" 2>&1 &
  else
    nohup python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > "$RUN_DIR/backend.log" 2>&1 &
  fi
  echo "$!" > "$RUN_DIR/backend.pid"
  STARTED_PID_FILES+=("$RUN_DIR/backend.pid")
fi

if [[ "$frontend_already_running" -eq 0 ]]; then
  echo "Starting Vue frontend..."
  (
    cd frontend
    if command -v setsid > /dev/null 2>&1; then
      nohup setsid npm run dev -- --host 0.0.0.0 --port 5173 > "$RUN_DIR/frontend.log" 2>&1 &
    else
      nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$RUN_DIR/frontend.log" 2>&1 &
    fi
    echo "$!" > "$RUN_DIR/frontend.pid"
  )
  STARTED_PID_FILES+=("$RUN_DIR/frontend.pid")
fi

sleep 2
if [[ "$backend_already_running" -eq 0 ]]; then
  if ! ps -p "$(cat "$RUN_DIR/backend.pid")" > /dev/null 2>&1; then
    echo "Backend process exited early. See .run/backend.log"
    stop_started_processes
    exit 1
  fi
fi
if [[ "$frontend_already_running" -eq 0 ]]; then
  if ! ps -p "$(cat "$RUN_DIR/frontend.pid")" > /dev/null 2>&1; then
    echo "Frontend process exited early. See .run/frontend.log"
    stop_started_processes
    exit 1
  fi
fi

wait_for_url "http://127.0.0.1:8000/api/health" "Backend" || true
wait_for_url "http://127.0.0.1:5173" "Frontend" || true

echo "Demo started."
print_access_urls

echo "Logs:"
echo "  backend: .run/backend.log"
echo "  frontend: .run/frontend.log"
