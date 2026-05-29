from pathlib import Path

import numpy as np
import pytest

from backend.app.data_loader import (
    get_fallback_simulated_dataset,
    load_portfolio_dataset,
    validate_portfolio_inputs,
)
from backend.app.pso_optimizer import run_pso


REQUIRED_FIELDS = {
    "data_source",
    "asset_names",
    "expected_returns",
    "covariance_matrix",
    "annualized",
    "trading_days_per_year",
    "source_notes",
}


def test_fallback_simulated_dataset_returns_required_fields():
    dataset = get_fallback_simulated_dataset(asset_count=10, random_seed=42)

    assert REQUIRED_FIELDS <= set(dataset)
    assert dataset["data_source"] == "simulated_fallback"
    assert len(dataset["asset_names"]) == 10
    assert dataset["expected_returns"].shape == (10,)
    assert dataset["covariance_matrix"].shape == (10, 10)
    assert "not real UCI data" in dataset["source_notes"]


def test_fallback_simulated_dataset_is_reproducible_with_fixed_seed():
    first = get_fallback_simulated_dataset(asset_count=8, random_seed=7)
    second = get_fallback_simulated_dataset(asset_count=8, random_seed=7)

    assert first["asset_names"] == second["asset_names"]
    np.testing.assert_allclose(first["expected_returns"], second["expected_returns"])
    np.testing.assert_allclose(first["covariance_matrix"], second["covariance_matrix"])


@pytest.mark.parametrize(
    ("expected_returns", "covariance_matrix", "message"),
    [
        ([0.1, np.nan], [[0.1, 0.0], [0.0, 0.2]], "expected_returns"),
        ([0.1, 0.2], [[0.1, np.inf], [0.0, 0.2]], "covariance_matrix"),
    ],
)
def test_validate_portfolio_inputs_rejects_nan_and_inf(
    expected_returns,
    covariance_matrix,
    message,
):
    with pytest.raises(ValueError, match=message):
        validate_portfolio_inputs(
            ["Strategy_1", "Strategy_2"],
            expected_returns,
            covariance_matrix,
        )


def test_validate_portfolio_inputs_rejects_covariance_dimension_mismatch():
    with pytest.raises(ValueError, match="N x N"):
        validate_portfolio_inputs(
            ["Strategy_1", "Strategy_2"],
            [0.1, 0.2],
            [[0.1, 0.0, 0.0], [0.0, 0.2, 0.0]],
        )


def test_validate_portfolio_inputs_rejects_negative_covariance_diagonal():
    with pytest.raises(ValueError, match="diagonal"):
        validate_portfolio_inputs(
            ["Strategy_1", "Strategy_2"],
            [0.1, 0.2],
            [[0.1, 0.0], [0.0, -0.2]],
        )


def test_load_portfolio_dataset_returns_required_fields():
    dataset = load_portfolio_dataset(random_seed=42)

    assert REQUIRED_FIELDS <= set(dataset)
    assert dataset["data_source"] in {"uci", "simulated_fallback"}
    assert len(dataset["asset_names"]) >= 2
    assert dataset["expected_returns"].ndim == 1
    assert dataset["covariance_matrix"].shape == (
        len(dataset["asset_names"]),
        len(dataset["asset_names"]),
    )
    validate_portfolio_inputs(
        dataset["asset_names"],
        dataset["expected_returns"],
        dataset["covariance_matrix"],
    )


def test_load_portfolio_dataset_output_can_run_pso():
    dataset = load_portfolio_dataset(random_seed=42)

    result = run_pso(
        dataset["expected_returns"],
        dataset["covariance_matrix"],
        particles=20,
        iterations=8,
        random_seed=42,
    )

    assert set(result) == {
        "best_weights",
        "objective_score",
        "expected_return",
        "volatility",
        "sharpe_ratio",
        "convergence_curve",
    }
    assert len(result["best_weights"]) == len(dataset["asset_names"])
    assert len(result["convergence_curve"]) == 8


def test_load_portfolio_dataset_falls_back_when_uci_file_is_missing(tmp_path):
    dataset = load_portfolio_dataset(raw_dir=Path(tmp_path), random_seed=11)

    assert dataset["data_source"] == "simulated_fallback"
    assert "not real UCI data" in dataset["source_notes"]
    validate_portfolio_inputs(
        dataset["asset_names"],
        dataset["expected_returns"],
        dataset["covariance_matrix"],
    )
