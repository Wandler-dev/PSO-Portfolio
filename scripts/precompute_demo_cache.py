"""Precompute demo preset optimization responses into the local file cache."""

from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backend.app.cache as cache
from backend.app.data_loader import load_portfolio_dataset
from backend.app.presets import DEMO_PRESETS
from backend.app.schemas import OptimizeRequest
from backend.app.services import run_optimization_service


def main():
    cache.clear_memory_cache()
    if cache.DEFAULT_CACHE_PATH.exists():
        cache.DEFAULT_CACHE_PATH.unlink()

    dataset = load_portfolio_dataset(random_seed=42)
    summaries = []
    for preset_name, preset in DEMO_PRESETS.items():
        request_for_key = OptimizeRequest(**preset)
        request_for_service = OptimizeRequest(preset_name=preset_name)
        result = run_optimization_service(request_for_service)
        cache_key = cache.build_cache_key(dataset, request_for_key)
        summaries.append(
            {
                "preset_name": preset_name,
                "expected_return": result["expected_return"],
                "volatility": result["volatility"],
                "sharpe_ratio": result["sharpe_ratio"],
                "selected_assets_count": len(result["selected_assets"]),
                "compute_time_seconds": result["compute_time_seconds"],
                "cache_key": cache_key,
            }
        )

    print(json.dumps(summaries, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
