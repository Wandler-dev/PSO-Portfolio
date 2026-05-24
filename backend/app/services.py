"""Service layer for portfolio data summaries and optimization workflows."""

from __future__ import annotations

from backend.app.data_loader import load_portfolio_dataset
from backend.app.pso_optimizer import run_pso
from backend.app.random_baseline import generate_random_portfolios
from backend.app.schemas import OptimizeRequest


SELECTED_THRESHOLD = 0.01


def build_data_summary():
    dataset = load_portfolio_dataset()
    return {
        "data_source": dataset["data_source"],
        "asset_count": len(dataset["asset_names"]),
        "annualized": dataset["annualized"],
        "trading_days_per_year": dataset["trading_days_per_year"],
        "asset_names": dataset["asset_names"],
        "source_notes": dataset["source_notes"],
    }


def build_selected_assets(asset_names, best_weights, threshold=SELECTED_THRESHOLD):
    selected_assets = []
    for asset_name, weight in zip(asset_names, best_weights, strict=True):
        if weight >= threshold:
            selected_assets.append(
                {
                    "asset_id": asset_name,
                    "weight": float(weight),
                }
            )
    return selected_assets


def build_asset_weight_table(asset_names, best_weights, threshold=SELECTED_THRESHOLD):
    rows = []
    for asset_name, weight in zip(asset_names, best_weights, strict=True):
        rows.append(
            {
                "asset_id": asset_name,
                "weight": float(weight),
                "selected": bool(weight >= threshold),
            }
        )
    return rows


def run_optimization_service(request: OptimizeRequest):
    dataset = load_portfolio_dataset(random_seed=request.random_seed)
    pso_result = run_pso(
        dataset["expected_returns"],
        dataset["covariance_matrix"],
        particles=request.particles,
        iterations=request.iterations,
        inertia_weight=request.inertia_weight,
        c1=request.c1,
        c2=request.c2,
        risk_free_rate=request.risk_free_rate,
        random_seed=request.random_seed,
    )
    baseline_points = generate_random_portfolios(
        dataset["expected_returns"],
        dataset["covariance_matrix"],
        samples=request.monte_carlo_samples,
        risk_free_rate=request.risk_free_rate,
        random_seed=request.random_seed,
    )
    risk_return_points = [
        {
            "volatility": point["volatility"],
            "expected_return": point["expected_return"],
            "sharpe_ratio": point["sharpe_ratio"],
            "type": "random",
        }
        for point in baseline_points
    ]
    best_point = {
        "volatility": pso_result["volatility"],
        "expected_return": pso_result["expected_return"],
        "sharpe_ratio": pso_result["sharpe_ratio"],
        "type": "pso_best",
    }

    return {
        "data_source": dataset["data_source"],
        "asset_count": len(dataset["asset_names"]),
        "expected_return": pso_result["expected_return"],
        "volatility": pso_result["volatility"],
        "sharpe_ratio": pso_result["sharpe_ratio"],
        "best_weights": pso_result["best_weights"],
        "selected_assets": build_selected_assets(
            dataset["asset_names"],
            pso_result["best_weights"],
        ),
        "convergence_curve": pso_result["convergence_curve"],
        "risk_return_points": risk_return_points,
        "best_point": best_point,
        "asset_weight_table": build_asset_weight_table(
            dataset["asset_names"],
            pso_result["best_weights"],
        ),
        "source_notes": dataset["source_notes"],
    }
