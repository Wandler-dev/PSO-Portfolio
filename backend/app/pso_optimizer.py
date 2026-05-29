"""Hand-written PSO optimizer for continuous portfolio weights."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.app.portfolio_math import (
    normalize_weights,
    portfolio_expected_return,
    portfolio_volatility,
    sharpe_ratio,
)


@dataclass(frozen=True)
class PSOResult:
    best_weights: np.ndarray
    objective_score: float
    expected_return: float
    volatility: float
    sharpe_ratio: float
    convergence_curve: list[dict[str, float]]

    def as_dict(self):
        return {
            "best_weights": self.best_weights.tolist(),
            "objective_score": self.objective_score,
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "convergence_curve": self.convergence_curve,
        }


def run_pso(
    expected_returns,
    covariance_matrix,
    particles=100,
    iterations=200,
    inertia_weight=0.7,
    c1=1.5,
    c2=1.5,
    risk_free_rate=0.0,
    random_seed=None,
    objective_mode="sharpe",
    risk_aversion=0.0,
    max_asset_weight=None,
    top_k_assets=None,
):
    expected_returns_array = np.asarray(expected_returns, dtype=float)
    covariance_array = np.asarray(covariance_matrix, dtype=float)
    _validate_inputs(
        expected_returns_array,
        covariance_array,
        particles,
        iterations,
        objective_mode,
        risk_aversion,
        max_asset_weight,
        top_k_assets,
    )

    rng = np.random.default_rng(random_seed)
    asset_count = expected_returns_array.shape[0]

    positions = rng.random((particles, asset_count))
    positions = _normalize_particle_matrix(
        positions,
        max_asset_weight=max_asset_weight,
        top_k_assets=top_k_assets,
    )
    velocities = rng.normal(loc=0.0, scale=0.05, size=(particles, asset_count))

    scores = np.array(
        [
            objective_score(
                position,
                expected_returns_array,
                covariance_array,
                risk_free_rate=risk_free_rate,
                objective_mode=objective_mode,
                risk_aversion=risk_aversion,
            )
            for position in positions
        ]
    )
    personal_best_positions = positions.copy()
    personal_best_scores = scores.copy()
    best_index = int(np.argmax(personal_best_scores))
    global_best_position = personal_best_positions[best_index].copy()
    global_best_score = float(personal_best_scores[best_index])

    convergence_curve = []

    for iteration in range(1, iterations + 1):
        r1 = rng.random((particles, asset_count))
        r2 = rng.random((particles, asset_count))
        velocities = (
            inertia_weight * velocities
            + c1 * r1 * (personal_best_positions - positions)
            + c2 * r2 * (global_best_position - positions)
        )
        positions = positions + velocities
        positions = _normalize_particle_matrix(
            positions,
            max_asset_weight=max_asset_weight,
            top_k_assets=top_k_assets,
        )

        scores = np.array(
            [
                objective_score(
                    position,
                    expected_returns_array,
                    covariance_array,
                    risk_free_rate=risk_free_rate,
                    objective_mode=objective_mode,
                    risk_aversion=risk_aversion,
                )
                for position in positions
            ]
        )

        improved = scores > personal_best_scores
        personal_best_positions[improved] = positions[improved]
        personal_best_scores[improved] = scores[improved]

        best_index = int(np.argmax(personal_best_scores))
        if personal_best_scores[best_index] > global_best_score:
            global_best_score = float(personal_best_scores[best_index])
            global_best_position = personal_best_positions[best_index].copy()

        convergence_curve.append(
            {
                "iteration": iteration,
                "objective_score": global_best_score,
                "sharpe_ratio": sharpe_ratio(
                    global_best_position,
                    expected_returns_array,
                    covariance_array,
                    risk_free_rate=risk_free_rate,
                ),
            }
        )

    best_weights = normalize_weights(
        global_best_position,
        max_weight=max_asset_weight,
        top_k=top_k_assets,
    )
    expected_return = portfolio_expected_return(best_weights, expected_returns_array)
    volatility = portfolio_volatility(best_weights, covariance_array)
    result_sharpe_ratio = sharpe_ratio(
        best_weights,
        expected_returns_array,
        covariance_array,
        risk_free_rate=risk_free_rate,
    )
    result = PSOResult(
        best_weights=best_weights,
        objective_score=objective_score(
            best_weights,
            expected_returns_array,
            covariance_array,
            risk_free_rate=risk_free_rate,
            objective_mode=objective_mode,
            risk_aversion=risk_aversion,
        ),
        expected_return=expected_return,
        volatility=volatility,
        sharpe_ratio=result_sharpe_ratio,
        convergence_curve=convergence_curve,
    )
    return result.as_dict()


def objective_score(
    weights,
    expected_returns,
    covariance_matrix,
    risk_free_rate=0.0,
    objective_mode="sharpe",
    risk_aversion=0.0,
):
    if objective_mode == "sharpe":
        return sharpe_ratio(
            weights,
            expected_returns,
            covariance_matrix,
            risk_free_rate=risk_free_rate,
        )
    if objective_mode == "risk_adjusted_return":
        expected_return = portfolio_expected_return(weights, expected_returns)
        volatility = portfolio_volatility(weights, covariance_matrix)
        return float(expected_return - risk_free_rate - risk_aversion * volatility)
    raise ValueError("objective_mode must be sharpe or risk_adjusted_return")


def _normalize_particle_matrix(positions, max_asset_weight=None, top_k_assets=None):
    return np.apply_along_axis(
        lambda row: normalize_weights(
            row,
            max_weight=max_asset_weight,
            top_k=top_k_assets,
        ),
        1,
        positions,
    )


def _validate_inputs(
    expected_returns,
    covariance_matrix,
    particles,
    iterations,
    objective_mode,
    risk_aversion,
    max_asset_weight,
    top_k_assets,
):
    if expected_returns.ndim != 1:
        raise ValueError("expected_returns must be a one-dimensional vector")
    if expected_returns.shape[0] < 2:
        raise ValueError("at least two assets are required")
    if covariance_matrix.shape != (expected_returns.shape[0], expected_returns.shape[0]):
        raise ValueError("covariance_matrix must be an N x N matrix")
    if particles <= 0:
        raise ValueError("particles must be positive")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if objective_mode not in {"sharpe", "risk_adjusted_return"}:
        raise ValueError("objective_mode must be sharpe or risk_adjusted_return")
    if risk_aversion < 0:
        raise ValueError("risk_aversion must be non-negative")
    if max_asset_weight is not None:
        if max_asset_weight <= 0 or max_asset_weight > 1:
            raise ValueError("max_asset_weight must be in the interval (0, 1]")
        active_count = expected_returns.shape[0] if top_k_assets is None else top_k_assets
        if max_asset_weight * active_count < 1.0:
            raise ValueError("max_asset_weight is too small for the active asset count")
    if top_k_assets is not None:
        if top_k_assets <= 0:
            raise ValueError("top_k_assets must be positive")
        if top_k_assets > expected_returns.shape[0]:
            raise ValueError("top_k_assets cannot exceed the asset count")
    if not np.all(np.isfinite(expected_returns)):
        raise ValueError("expected_returns must contain only finite values")
    if not np.all(np.isfinite(covariance_matrix)):
        raise ValueError("covariance_matrix must contain only finite values")
