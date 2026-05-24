import math

import numpy as np
import pytest
from pydantic import ValidationError

import backend.app.services as services
from backend.app.main import app
from backend.app.schemas import OptimizeRequest


REQUIRED_OPTIMIZE_FIELDS = {
    "data_source",
    "asset_count",
    "expected_return",
    "volatility",
    "sharpe_ratio",
    "best_weights",
    "selected_assets",
    "convergence_curve",
    "risk_return_points",
    "best_point",
    "asset_weight_table",
    "source_notes",
}


def small_dataset():
    return {
        "data_source": "uci",
        "asset_names": ["Strategy_1", "Strategy_2", "Strategy_3"],
        "expected_returns": np.array([0.10, 0.14, 0.08]),
        "covariance_matrix": np.array(
            [
                [0.050, 0.010, 0.004],
                [0.010, 0.070, 0.006],
                [0.004, 0.006, 0.040],
            ]
        ),
        "annualized": True,
        "trading_days_per_year": None,
        "source_notes": "test dataset",
    }


@pytest.fixture(autouse=True)
def patch_dataset(monkeypatch):
    monkeypatch.setattr(services, "load_portfolio_dataset", lambda *args, **kwargs: small_dataset())


@pytest.fixture
def optimize_request():
    return OptimizeRequest(
        particles=20,
        iterations=50,
        inertia_weight=0.7,
        c1=1.5,
        c2=1.5,
        risk_free_rate=0.0,
        random_seed=42,
        monte_carlo_samples=2000,
    )


@pytest.fixture
def optimize_result(optimize_request):
    return services.run_optimization_service(optimize_request)


def test_valid_optimize_request_can_be_created():
    request = OptimizeRequest()

    assert request.particles == 100
    assert request.iterations == 200
    assert request.inertia_weight == 0.7
    assert request.c1 == 1.5
    assert request.c2 == 1.5
    assert request.risk_free_rate == 0.0
    assert request.random_seed == 42
    assert request.monte_carlo_samples == 3000


@pytest.mark.parametrize(
    "field_overrides",
    [
        {"particles": 19},
        {"iterations": 49},
        {"monte_carlo_samples": 1999},
    ],
)
def test_optimize_request_rejects_invalid_ranges(field_overrides):
    with pytest.raises(ValidationError):
        OptimizeRequest(**field_overrides)


def test_build_data_summary_returns_data_source_and_asset_count():
    summary = services.build_data_summary()

    assert summary["data_source"] == "uci"
    assert summary["asset_count"] == 3
    assert summary["asset_count"] == len(summary["asset_names"])
    assert summary["annualized"] is True
    assert "source_notes" in summary


def test_run_optimization_service_returns_required_fields(optimize_result):
    assert REQUIRED_OPTIMIZE_FIELDS <= set(optimize_result)


def test_run_optimization_service_best_weights_match_asset_count(optimize_result):
    assert len(optimize_result["best_weights"]) == optimize_result["asset_count"]
    assert math.isclose(
        sum(optimize_result["best_weights"]),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-6,
    )


def test_run_optimization_service_generates_requested_random_points(optimize_result):
    assert len(optimize_result["risk_return_points"]) >= 2000
    first_point = optimize_result["risk_return_points"][0]
    assert {"volatility", "expected_return", "sharpe_ratio", "type"} <= set(first_point)
    assert first_point["type"] == "random"


def test_run_optimization_service_selected_assets_use_threshold(optimize_result):
    assert all(asset["weight"] >= 0.01 for asset in optimize_result["selected_assets"])


def test_asset_weight_table_selected_matches_threshold(optimize_result):
    for row in optimize_result["asset_weight_table"]:
        assert row["selected"] is (row["weight"] >= 0.01)


def test_best_point_has_expected_fields(optimize_result):
    best_point = optimize_result["best_point"]

    assert {"volatility", "expected_return", "sharpe_ratio", "type"} <= set(best_point)
    assert best_point["type"] == "pso_best"


def test_top_level_response_excludes_forbidden_field_names(optimize_result):
    assert "risk" not in optimize_result
    assert "sigma_p" not in optimize_result
    assert "best_sharpe" not in optimize_result


def test_main_app_registers_required_routes():
    paths = {route.path for route in app.routes}

    assert "/api/health" in paths
    assert "/api/data/summary" in paths
    assert "/api/optimize" in paths
