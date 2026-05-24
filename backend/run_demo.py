"""Run the Stage 1 PSO portfolio optimization demo with simulated data."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.pso_optimizer import run_pso
from backend.app.random_baseline import generate_random_portfolios


def build_simulated_problem(random_seed=42, asset_count=10):
    rng = np.random.default_rng(random_seed)
    expected_returns = rng.uniform(0.06, 0.20, size=asset_count)
    factor_loadings = rng.normal(size=(asset_count, asset_count))
    covariance_matrix = (factor_loadings @ factor_loadings.T) / asset_count
    covariance_matrix = covariance_matrix * 0.015
    covariance_matrix += np.eye(asset_count) * 0.02
    return expected_returns, covariance_matrix


def selected_assets_from_weights(best_weights, threshold=0.01):
    selected_assets = []
    for index, weight in enumerate(best_weights, start=1):
        if weight >= threshold:
            selected_assets.append(
                {
                    "asset_id": f"Asset_{index}",
                    "weight": float(weight),
                }
            )
    return selected_assets


def main():
    random_seed = 42
    expected_returns, covariance_matrix = build_simulated_problem(
        random_seed=random_seed,
        asset_count=10,
    )

    pso_result = run_pso(
        expected_returns,
        covariance_matrix,
        particles=80,
        iterations=120,
        inertia_weight=0.7,
        c1=1.5,
        c2=1.5,
        risk_free_rate=0.0,
        random_seed=random_seed,
    )
    baseline = generate_random_portfolios(
        expected_returns,
        covariance_matrix,
        samples=3000,
        risk_free_rate=0.0,
        random_seed=random_seed,
    )
    selected_assets = selected_assets_from_weights(pso_result["best_weights"])

    output = {
        "data_source": "simulated",
        "asset_count": len(expected_returns),
        "best_weights": pso_result["best_weights"],
        "expected_return": pso_result["expected_return"],
        "volatility": pso_result["volatility"],
        "sharpe_ratio": pso_result["sharpe_ratio"],
        "selected_assets": selected_assets,
        "convergence_points": len(pso_result["convergence_curve"]),
        "monte_carlo_points": len(baseline),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
