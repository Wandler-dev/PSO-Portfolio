"""Smoke test the FastAPI backend through a real uvicorn process."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"
STARTUP_TIMEOUT_SECONDS = 20
REQUEST_TIMEOUT_SECONDS = 180


def request_json(path, method="GET", payload=None):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_server(process):
    deadline = time.time() + STARTUP_TIMEOUT_SECONDS
    last_error = None
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("uvicorn exited before serving requests")
        try:
            return request_json("/api/health")
        except (HTTPError, URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"uvicorn did not become ready: {last_error}")


def terminate_process(process):
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main():
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        health = wait_for_server(process)
        summary = request_json("/api/data/summary")
        presets = request_json("/api/presets")
        optimize_payload = {
            "particles": 20,
            "iterations": 50,
            "inertia_weight": 0.7,
            "c1": 1.5,
            "c2": 1.5,
            "risk_free_rate": 0.0,
            "random_seed": 42,
            "monte_carlo_samples": 2000,
        }
        optimize = request_json(
            "/api/optimize",
            method="POST",
            payload=optimize_payload,
        )
        preset_payload = {"preset_name": "balanced"}
        first_preset_optimize = request_json(
            "/api/optimize",
            method="POST",
            payload=preset_payload,
        )
        second_preset_optimize = request_json(
            "/api/optimize",
            method="POST",
            payload=preset_payload,
        )
        if len(presets) != 3:
            raise RuntimeError(f"expected 3 presets, got {len(presets)}")
        if len(optimize["risk_return_points"]) < optimize_payload["monte_carlo_samples"]:
            raise RuntimeError("risk_return_points count is smaller than requested")
        if second_preset_optimize["cache_hit"] is not True:
            raise RuntimeError("second balanced preset optimization did not hit cache")

        output = {
            "health.status": health["status"],
            "summary.data_source": summary["data_source"],
            "summary.asset_count": summary["asset_count"],
            "presets.count": len(presets),
            "optimize.expected_return": optimize["expected_return"],
            "optimize.volatility": optimize["volatility"],
            "optimize.sharpe_ratio": optimize["sharpe_ratio"],
            "len(optimize.best_weights)": len(optimize["best_weights"]),
            "len(optimize.risk_return_points)": len(optimize["risk_return_points"]),
            "first_optimize.cache_hit": first_preset_optimize["cache_hit"],
            "second_optimize.cache_hit": second_preset_optimize["cache_hit"],
            "first_optimize.compute_time_seconds": first_preset_optimize["compute_time_seconds"],
            "second_optimize.compute_time_seconds": second_preset_optimize["compute_time_seconds"],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"smoke_api failed: {exc}", file=sys.stderr)
        terminate_process(process)
        if process.stdout is not None:
            logs = process.stdout.read()
            if logs:
                print(logs, file=sys.stderr)
        return 1
    finally:
        terminate_process(process)


if __name__ == "__main__":
    raise SystemExit(main())
