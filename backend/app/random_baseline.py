"""Monte Carlo random portfolio baseline for risk-return scatter plots."""

from __future__ import annotations

import numpy as np

from backend.app.portfolio_math import (
    normalize_weights,
    portfolio_expected_return,
    portfolio_volatility,
    sharpe_ratio,
)


def generate_random_portfolios(
    expected_returns,
    covariance_matrix,
    samples=3000,
    risk_free_rate=0.0,
    random_seed=None,
):
    if samples < 2000:
        raise ValueError("samples must be at least 2000")

    expected_returns_array = np.asarray(expected_returns, dtype=float)
    covariance_array = np.asarray(covariance_matrix, dtype=float)
    if expected_returns_array.ndim != 1:
        raise ValueError("expected_returns must be a one-dimensional vector")
    if covariance_array.shape != (
        expected_returns_array.shape[0],
        expected_returns_array.shape[0],
    ):
        raise ValueError("covariance_matrix must be an N x N matrix")

    rng = np.random.default_rng(random_seed)
    raw_weights = rng.random((samples, expected_returns_array.shape[0]))
    weights = np.apply_along_axis(normalize_weights, 1, raw_weights)

    portfolios = []
    for weight_vector in weights:
        portfolios.append(
            {
                "volatility": portfolio_volatility(weight_vector, covariance_array),
                "expected_return": portfolio_expected_return(
                    weight_vector,
                    expected_returns_array,
                ),
                "sharpe_ratio": sharpe_ratio(
                    weight_vector,
                    expected_returns_array,
                    covariance_array,
                    risk_free_rate=risk_free_rate,
                ),
            }
        )
    return portfolios
