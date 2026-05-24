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
    expected_return: float
    volatility: float
    sharpe_ratio: float
    convergence_curve: list[dict[str, float]]

    def as_dict(self):
        return {
            "best_weights": self.best_weights.tolist(),
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
):
    expected_returns_array = np.asarray(expected_returns, dtype=float)
    covariance_array = np.asarray(covariance_matrix, dtype=float)
    _validate_inputs(
        expected_returns_array,
        covariance_array,
        particles,
        iterations,
    )

    rng = np.random.default_rng(random_seed)
    asset_count = expected_returns_array.shape[0]

    positions = rng.random((particles, asset_count))
    positions = np.apply_along_axis(normalize_weights, 1, positions)
    velocities = rng.normal(loc=0.0, scale=0.05, size=(particles, asset_count))

    scores = np.array(
        [
            sharpe_ratio(
                position,
                expected_returns_array,
                covariance_array,
                risk_free_rate=risk_free_rate,
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
        positions = np.apply_along_axis(normalize_weights, 1, positions)

        scores = np.array(
            [
                sharpe_ratio(
                    position,
                    expected_returns_array,
                    covariance_array,
                    risk_free_rate=risk_free_rate,
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
                "sharpe_ratio": global_best_score,
            }
        )

    best_weights = normalize_weights(global_best_position)
    result = PSOResult(
        best_weights=best_weights,
        expected_return=portfolio_expected_return(best_weights, expected_returns_array),
        volatility=portfolio_volatility(best_weights, covariance_array),
        sharpe_ratio=sharpe_ratio(
            best_weights,
            expected_returns_array,
            covariance_array,
            risk_free_rate=risk_free_rate,
        ),
        convergence_curve=convergence_curve,
    )
    return result.as_dict()


def _validate_inputs(expected_returns, covariance_matrix, particles, iterations):
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
    if not np.all(np.isfinite(expected_returns)):
        raise ValueError("expected_returns must contain only finite values")
    if not np.all(np.isfinite(covariance_matrix)):
        raise ValueError("covariance_matrix must contain only finite values")
