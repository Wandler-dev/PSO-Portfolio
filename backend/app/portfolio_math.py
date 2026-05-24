"""Portfolio math helpers for the Stage 1 PSO prototype."""

from __future__ import annotations

import math

import numpy as np


NEAR_ZERO = 1e-12


def normalize_weights(weights):
    """Clip weights to non-negative values and normalize them to sum to one."""
    values = np.asarray(weights, dtype=float)
    if values.ndim != 1:
        raise ValueError("weights must be a one-dimensional vector")
    if values.size == 0:
        raise ValueError("weights must not be empty")
    if not np.all(np.isfinite(values)):
        raise ValueError("weights must contain only finite values")

    clipped = np.clip(values, 0.0, None)
    total = float(clipped.sum())
    if total <= NEAR_ZERO:
        return np.full(values.shape, 1.0 / values.size, dtype=float)
    return clipped / total


def portfolio_expected_return(weights, expected_returns):
    normalized_weights = normalize_weights(weights)
    returns = np.asarray(expected_returns, dtype=float)
    _validate_vector_pair(normalized_weights, returns)
    return float(normalized_weights @ returns)


def portfolio_volatility(weights, covariance_matrix):
    normalized_weights = normalize_weights(weights)
    covariance = np.asarray(covariance_matrix, dtype=float)
    _validate_covariance(normalized_weights, covariance)
    variance = float(normalized_weights.T @ covariance @ normalized_weights)
    return math.sqrt(max(variance, 0.0))


def sharpe_ratio(weights, expected_returns, covariance_matrix, risk_free_rate=0.0):
    expected_return = portfolio_expected_return(weights, expected_returns)
    volatility = portfolio_volatility(weights, covariance_matrix)
    if volatility <= NEAR_ZERO:
        return 0.0
    return float((expected_return - risk_free_rate) / volatility)


def _validate_vector_pair(weights, expected_returns):
    if expected_returns.ndim != 1:
        raise ValueError("expected_returns must be a one-dimensional vector")
    if weights.shape[0] != expected_returns.shape[0]:
        raise ValueError("weights and expected_returns must have the same length")
    if not np.all(np.isfinite(expected_returns)):
        raise ValueError("expected_returns must contain only finite values")


def _validate_covariance(weights, covariance_matrix):
    if covariance_matrix.ndim != 2:
        raise ValueError("covariance_matrix must be a two-dimensional matrix")
    if covariance_matrix.shape != (weights.shape[0], weights.shape[0]):
        raise ValueError("covariance_matrix shape must match weights length")
    if not np.all(np.isfinite(covariance_matrix)):
        raise ValueError("covariance_matrix must contain only finite values")
