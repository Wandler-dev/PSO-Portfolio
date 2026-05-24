#!/usr/bin/env bash
set -euo pipefail

stop_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "$name: no pid file found ($pid_file)"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]]; then
    echo "$name: pid file is empty; removing $pid_file"
    rm -f "$pid_file"
    return 0
  fi

  if ps -p "$pid" > /dev/null 2>&1; then
    echo "$name: stopping pid $pid"
    kill -- "-$pid" 2>/dev/null || kill "$pid" || true
    sleep 1
    if kill -0 "-$pid" 2>/dev/null || ps -p "$pid" > /dev/null 2>&1; then
      echo "$name: pid $pid is still running; please inspect it manually"
    else
      echo "$name: stopped"
    fi
  else
    if kill -0 "-$pid" 2>/dev/null; then
      echo "$name: stopping stale process group $pid"
      kill -- "-$pid" 2>/dev/null || true
      sleep 1
      if kill -0 "-$pid" 2>/dev/null; then
        echo "$name: process group $pid is still running; please inspect it manually"
      else
        echo "$name: stopped"
      fi
    else
      echo "$name: pid $pid is not running"
    fi
  fi

  rm -f "$pid_file"
}

stop_pid_file "backend" ".run/backend.pid"
stop_pid_file "frontend" ".run/frontend.pid"
