"""Two-level optimization response cache for demo API calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_PATH = PROJECT_ROOT / "data" / "cache" / "optimization_cache.json"

_MEMORY_CACHE: dict[str, dict] = {}


def build_cache_key(dataset_summary_or_dataset, request):
    payload = {
        "data_source": dataset_summary_or_dataset["data_source"],
        "asset_count": len(dataset_summary_or_dataset.get("asset_names", []))
        or dataset_summary_or_dataset.get("asset_count"),
        "particles": request.particles,
        "iterations": request.iterations,
        "inertia_weight": request.inertia_weight,
        "c1": request.c1,
        "c2": request.c2,
        "risk_free_rate": request.risk_free_rate,
        "random_seed": request.random_seed,
        "monte_carlo_samples": request.monte_carlo_samples,
    }
    dataset_signature = dataset_summary_or_dataset.get("dataset_signature")
    if dataset_signature is not None:
        payload["dataset_signature"] = dataset_signature

    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_cached_response(cache_key):
    if cache_key in _MEMORY_CACHE:
        return _MEMORY_CACHE[cache_key]

    file_cache = load_file_cache()
    cached_response = file_cache.get(cache_key)
    if cached_response is not None:
        _MEMORY_CACHE[cache_key] = cached_response
    return cached_response


def set_cached_response(cache_key, response):
    _MEMORY_CACHE[cache_key] = response
    file_cache = load_file_cache()
    file_cache[cache_key] = response
    save_file_cache(file_cache)


def load_file_cache():
    if not DEFAULT_CACHE_PATH.exists():
        return {}
    try:
        with DEFAULT_CACHE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_file_cache(cache_data=None):
    data = _MEMORY_CACHE if cache_data is None else cache_data
    DEFAULT_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_CACHE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def clear_memory_cache():
    _MEMORY_CACHE.clear()


def cache_size():
    return len(_MEMORY_CACHE)
