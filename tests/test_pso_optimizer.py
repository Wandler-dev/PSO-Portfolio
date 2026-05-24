from pathlib import Path

import numpy as np
import pytest

from backend.app.portfolio_math import normalize_weights
from backend.app.pso_optimizer import run_pso
from backend.app.random_baseline import generate_random_portfolios


def sample_problem():
    expected_returns = np.array([0.08, 0.12, 0.16, 0.10])
    covariance_matrix = np.array(
        [
            [0.050, 0.010, 0.006, 0.004],
            [0.010, 0.070, 0.012, 0.006],
            [0.006, 0.012, 0.090, 0.008],
            [0.004, 0.006, 0.008, 0.060],
        ]
    )
    return expected_returns, covariance_matrix


def test_run_pso_returns_required_fields_and_valid_best_weights():
    expected_returns, covariance_matrix = sample_problem()

    result = run_pso(
        expected_returns,
        covariance_matrix,
        particles=30,
        iterations=25,
        inertia_weight=0.7,
        c1=1.5,
        c2=1.5,
        risk_free_rate=0.0,
        random_seed=42,
    )

    assert set(result) == {
        "best_weights",
        "expected_return",
        "volatility",
        "sharpe_ratio",
        "convergence_curve",
    }
    assert len(result["best_weights"]) == len(expected_returns)
    assert min(result["best_weights"]) >= -1e-12
    assert sum(result["best_weights"]) == pytest_approx(1.0)
    assert len(result["convergence_curve"]) == 25


def test_run_pso_is_reproducible_with_fixed_random_seed():
    expected_returns, covariance_matrix = sample_problem()

    first = run_pso(
        expected_returns,
        covariance_matrix,
        particles=25,
        iterations=20,
        inertia_weight=0.6,
        c1=1.4,
        c2=1.6,
        risk_free_rate=0.01,
        random_seed=7,
    )
    second = run_pso(
        expected_returns,
        covariance_matrix,
        particles=25,
        iterations=20,
        inertia_weight=0.6,
        c1=1.4,
        c2=1.6,
        risk_free_rate=0.01,
        random_seed=7,
    )

    np.testing.assert_allclose(first["best_weights"], second["best_weights"])
    assert first["sharpe_ratio"] == pytest_approx(second["sharpe_ratio"])


def test_generate_random_portfolios_defaults_to_at_least_2000_points():
    expected_returns, covariance_matrix = sample_problem()

    portfolios = generate_random_portfolios(
        expected_returns,
        covariance_matrix,
        risk_free_rate=0.0,
        random_seed=10,
    )

    assert len(portfolios) >= 2000
    assert {"volatility", "expected_return", "sharpe_ratio"} <= set(portfolios[0])


def test_normalize_weights_rejects_nan_and_inf_values():
    for weights in (
        np.array([0.5, np.nan, 0.5]),
        np.array([0.5, np.inf, 0.5]),
        np.array([0.5, -np.inf, 0.5]),
    ):
        with pytest.raises(ValueError):
            normalize_weights(weights)


def test_forbidden_optimization_libraries_are_not_imported():
    forbidden_names = ("scipy.optimize", "pyswarms")
    source_paths = [
        Path("backend/app/data_loader.py"),
        Path("backend/app/portfolio_math.py"),
        Path("backend/app/pso_optimizer.py"),
        Path("backend/app/random_baseline.py"),
    ]

    for source_path in source_paths:
        if not source_path.exists():
            continue
        source = source_path.read_text(encoding="utf-8")
        for forbidden_name in forbidden_names:
            assert forbidden_name not in source


def pytest_approx(value):
    import pytest

    return pytest.approx(value)
