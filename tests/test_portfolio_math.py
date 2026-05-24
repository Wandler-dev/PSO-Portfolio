import math

import numpy as np

from backend.app.portfolio_math import (
    normalize_weights,
    portfolio_expected_return,
    portfolio_volatility,
    sharpe_ratio,
)


def test_normalize_weights_makes_weights_non_negative_and_sum_to_one():
    weights = np.array([-1.0, 2.0, 3.0])

    normalized = normalize_weights(weights)

    assert np.all(normalized >= 0.0)
    assert normalized.sum() == pytest_approx(1.0)
    np.testing.assert_allclose(normalized, np.array([0.0, 0.4, 0.6]))


def test_normalize_weights_uses_uniform_weights_when_all_values_are_zero_after_clipping():
    weights = np.array([-2.0, 0.0, -1.0])

    normalized = normalize_weights(weights)

    np.testing.assert_allclose(normalized, np.array([1 / 3, 1 / 3, 1 / 3]))


def test_portfolio_expected_return_uses_weighted_sum():
    weights = np.array([0.25, 0.75])
    expected_returns = np.array([0.08, 0.16])

    result = portfolio_expected_return(weights, expected_returns)

    assert result == pytest_approx(0.14)


def test_portfolio_volatility_uses_quadratic_covariance_formula():
    weights = np.array([0.25, 0.75])
    covariance_matrix = np.array([[0.04, 0.006], [0.006, 0.09]])

    result = portfolio_volatility(weights, covariance_matrix)

    expected = math.sqrt(float(weights.T @ covariance_matrix @ weights))
    assert result == pytest_approx(expected)


def test_sharpe_ratio_uses_excess_return_divided_by_volatility():
    weights = np.array([0.4, 0.6])
    expected_returns = np.array([0.10, 0.20])
    covariance_matrix = np.array([[0.04, 0.0], [0.0, 0.09]])
    risk_free_rate = 0.03

    result = sharpe_ratio(
        weights,
        expected_returns,
        covariance_matrix,
        risk_free_rate=risk_free_rate,
    )

    expected_return = float(weights @ expected_returns)
    volatility = math.sqrt(float(weights.T @ covariance_matrix @ weights))
    assert result == pytest_approx((expected_return - risk_free_rate) / volatility)


def test_sharpe_ratio_returns_zero_when_volatility_is_near_zero():
    weights = np.array([0.5, 0.5])
    expected_returns = np.array([0.10, 0.12])
    covariance_matrix = np.zeros((2, 2))

    result = sharpe_ratio(weights, expected_returns, covariance_matrix)

    assert result == pytest_approx(0.0)


def pytest_approx(value):
    import pytest

    return pytest.approx(value)
