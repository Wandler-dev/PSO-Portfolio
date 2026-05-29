"""Portfolio math helpers for the Stage 1 PSO prototype."""

from __future__ import annotations

import math

import numpy as np


NEAR_ZERO = 1e-12


def normalize_weights(weights, max_weight=None, top_k=None):
    """Clip weights to a valid long-only, fully-invested portfolio."""
    values = np.asarray(weights, dtype=float)
    if values.ndim != 1:
        raise ValueError("weights must be a one-dimensional vector")
    if values.size == 0:
        raise ValueError("weights must not be empty")
    if not np.all(np.isfinite(values)):
        raise ValueError("weights must contain only finite values")
    if top_k is not None:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if top_k > values.size:
            raise ValueError("top_k cannot exceed weights length")
    if max_weight is not None:
        if max_weight <= 0 or max_weight > 1:
            raise ValueError("max_weight must be in the interval (0, 1]")
        active_count = values.size if top_k is None else top_k
        if max_weight * active_count < 1.0 - NEAR_ZERO:
            raise ValueError("max_weight is too small for the active asset count")

    active_mask = np.ones(values.shape, dtype=bool)
    if top_k is not None and top_k < values.size:
        active_mask[:] = False
        active_indices = np.argpartition(values, -top_k)[-top_k:]
        active_mask[active_indices] = True

    clipped = np.where(active_mask, np.clip(values, 0.0, None), 0.0)
    total = float(clipped.sum())
    if total <= NEAR_ZERO:
        result = np.zeros(values.shape, dtype=float)
        if top_k is None:
            result[:] = 1.0 / values.size
            return _apply_max_weight(result, max_weight, active_mask)
        result[active_mask] = 1.0 / top_k
        return _apply_max_weight(result, max_weight, active_mask)
    normalized = clipped / total
    return _apply_max_weight(normalized, max_weight, active_mask)


def _apply_max_weight(weights, max_weight, active_mask):
    if max_weight is None:
        return weights

    capped = np.where(active_mask, np.clip(weights, 0.0, None), 0.0)
    fixed = np.zeros(capped.shape, dtype=bool)
    remaining_weight = 1.0

    for _ in range(capped.size + 1):
        available = active_mask & ~fixed
        if not np.any(available):
            if abs(float(capped.sum()) - 1.0) <= 1e-8:
                return capped
            raise ValueError("max_weight is infeasible for the active asset set")

        subtotal = float(capped[available].sum())
        if subtotal <= NEAR_ZERO:
            capped[available] = remaining_weight / int(np.sum(available))
        else:
            capped[available] = capped[available] / subtotal * remaining_weight

        above_cap = available & (capped > max_weight)
        if not np.any(above_cap):
            capped[~active_mask] = 0.0
            return capped / capped.sum()

        capped[above_cap] = max_weight
        fixed[above_cap] = True
        remaining_weight = 1.0 - float(capped[fixed].sum())
        if remaining_weight <= NEAR_ZERO:
            capped[active_mask & ~fixed] = 0.0
            return capped / capped.sum()

    raise ValueError("failed to apply max_weight constraint")


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
