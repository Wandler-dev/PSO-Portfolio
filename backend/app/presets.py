"""Demo preset parameter sets for portfolio optimization."""

from __future__ import annotations


DEMO_PRESETS = {
    "conservative": {
        "preset_name": "conservative",
        "particles": 50,
        "iterations": 150,
        "inertia_weight": 0.5,
        "c1": 1.2,
        "c2": 1.8,
        "risk_free_rate": 0.0,
        "random_seed": 42,
        "monte_carlo_samples": 3000,
    },
    "balanced": {
        "preset_name": "balanced",
        "particles": 100,
        "iterations": 200,
        "inertia_weight": 0.7,
        "c1": 1.5,
        "c2": 1.5,
        "risk_free_rate": 0.0,
        "random_seed": 42,
        "monte_carlo_samples": 3000,
    },
    "aggressive": {
        "preset_name": "aggressive",
        "particles": 200,
        "iterations": 400,
        "inertia_weight": 0.9,
        "c1": 2.0,
        "c2": 1.2,
        "risk_free_rate": 0.0,
        "random_seed": 42,
        "monte_carlo_samples": 3000,
    },
}


def list_presets():
    return [dict(preset) for preset in DEMO_PRESETS.values()]


def get_preset(preset_name):
    if preset_name is None:
        return None
    return DEMO_PRESETS.get(preset_name)
