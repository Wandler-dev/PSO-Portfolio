"""Run Stage 2 data loading and validate it with the Stage 1 PSO optimizer."""

from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.data_loader import load_portfolio_dataset
from backend.app.pso_optimizer import run_pso


def selected_assets_count(best_weights, threshold=0.01):
    return sum(1 for weight in best_weights if weight >= threshold)


def main():
    random_seed = 42
    dataset = load_portfolio_dataset(random_seed=random_seed)

    result = run_pso(
        dataset["expected_returns"],
        dataset["covariance_matrix"],
        particles=80,
        iterations=120,
        inertia_weight=0.7,
        c1=1.5,
        c2=1.5,
        risk_free_rate=0.0,
        random_seed=random_seed,
    )

    output = {
        "data_source": dataset["data_source"],
        "asset_count": len(dataset["asset_names"]),
        "annualized": dataset["annualized"],
        "trading_days_per_year": dataset["trading_days_per_year"],
        "expected_returns_head": dataset["expected_returns"][:5].tolist(),
        "covariance_matrix_shape": list(dataset["covariance_matrix"].shape),
        "source_notes": dataset["source_notes"],
        "expected_return": result["expected_return"],
        "volatility": result["volatility"],
        "sharpe_ratio": result["sharpe_ratio"],
        "selected_assets_count": selected_assets_count(result["best_weights"]),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
