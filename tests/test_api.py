import math

import numpy as np
import pytest
from pydantic import ValidationError

import backend.app.cache as cache
import backend.app.services as services
from backend.app.main import app
from backend.app.presets import DEMO_PRESETS
from backend.app.schemas import OptimizeRequest


REQUIRED_OPTIMIZE_FIELDS = {
    "data_source",
    "asset_count",
    "expected_return",
    "volatility",
    "sharpe_ratio",
    "objective_score",
    "objective_mode",
    "risk_aversion",
    "max_asset_weight",
    "top_k_assets",
    "best_weights",
    "selected_assets",
    "convergence_curve",
    "risk_return_points",
    "best_point",
    "asset_weight_table",
    "source_notes",
    "cache_hit",
    "preset_name",
    "compute_time_seconds",
}


def small_dataset():
    asset_count = 10
    return {
        "data_source": "uci",
        "asset_names": [f"Strategy_{index}" for index in range(1, asset_count + 1)],
        "expected_returns": np.linspace(0.08, 0.16, asset_count),
        "covariance_matrix": np.eye(asset_count) * 0.05,
        "annualized": True,
        "trading_days_per_year": None,
        "source_notes": "test dataset",
    }


@pytest.fixture(autouse=True)
def patch_dataset_and_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(services, "load_portfolio_dataset", lambda *args, **kwargs: small_dataset())
    monkeypatch.setattr(cache, "DEFAULT_CACHE_PATH", tmp_path / "optimization_cache.json")
    cache.clear_memory_cache()


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
    assert request.objective_mode == "sharpe"
    assert request.risk_aversion == 0.0
    assert request.max_asset_weight is None
    assert request.top_k_assets is None
    assert request.random_seed == 42
    assert request.monte_carlo_samples == 3000
    assert request.preset_name is None


@pytest.mark.parametrize(
    "field_overrides",
    [
        {"particles": 19},
        {"iterations": 49},
        {"monte_carlo_samples": 1999},
        {"preset_name": "invalid"},
        {"objective_mode": "invalid"},
        {"risk_aversion": -0.1},
        {"max_asset_weight": 1.1},
        {"top_k_assets": 1},
        {"max_asset_weight": 0.25, "top_k_assets": 3},
    ],
)
def test_optimize_request_rejects_invalid_ranges(field_overrides):
    with pytest.raises(ValidationError):
        OptimizeRequest(**field_overrides)


def test_build_data_summary_returns_data_source_and_asset_count():
    summary = services.build_data_summary()

    assert summary["data_source"] == "uci"
    assert summary["asset_count"] == 10
    assert summary["asset_count"] == len(summary["asset_names"])
    assert summary["annualized"] is True
    assert "source_notes" in summary


def test_run_optimization_service_returns_required_fields(optimize_result):
    assert REQUIRED_OPTIMIZE_FIELDS <= set(optimize_result)
    assert optimize_result["cache_hit"] is False
    assert optimize_result["preset_name"] is None
    assert optimize_result["compute_time_seconds"] >= 0


def test_same_request_second_call_hits_cache(optimize_request):
    first = services.run_optimization_service(optimize_request)
    second = services.run_optimization_service(optimize_request)

    assert first["cache_hit"] is False
    assert second["cache_hit"] is True
    assert REQUIRED_OPTIMIZE_FIELDS <= set(second)


def test_run_optimization_service_best_weights_match_asset_count(optimize_result):
    assert len(optimize_result["best_weights"]) == optimize_result["asset_count"]
    assert math.isclose(
        sum(optimize_result["best_weights"]),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-6,
    )


def test_run_optimization_service_respects_weight_and_top_k_constraints():
    request = OptimizeRequest(
        particles=20,
        iterations=50,
        max_asset_weight=0.5,
        top_k_assets=2,
        monte_carlo_samples=2000,
    )

    result = services.run_optimization_service(request)

    assert result["max_asset_weight"] == 0.5
    assert result["top_k_assets"] == 2
    assert max(result["best_weights"]) <= 0.5000001
    assert sum(weight > 1e-12 for weight in result["best_weights"]) <= 2


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
    assert "/api/presets" in paths


def test_balanced_preset_runs_and_marks_preset_name():
    request = OptimizeRequest(preset_name="balanced")

    result = services.run_optimization_service(request)

    assert result["preset_name"] == "balanced"
    assert len(result["convergence_curve"]) == DEMO_PRESETS["balanced"]["iterations"]


def test_all_demo_presets_exist():
    assert set(DEMO_PRESETS) == {"conservative", "balanced", "aggressive"}
