"""Request schemas for the FastAPI portfolio optimization API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.presets import DEMO_PRESETS


class OptimizeRequest(BaseModel):
    preset_name: str | None = None
    particles: int = Field(default=100, ge=20, le=300)
    iterations: int = Field(default=200, ge=50, le=500)
    inertia_weight: float = Field(default=0.7, ge=0.1, le=1.5)
    c1: float = Field(default=1.5, ge=0.5, le=3.0)
    c2: float = Field(default=1.5, ge=0.5, le=3.0)
    risk_free_rate: float = 0.0
    objective_mode: str = "sharpe"
    risk_aversion: float = Field(default=0.0, ge=0.0, le=5.0)
    max_asset_weight: float | None = Field(default=None, gt=0.0, le=1.0)
    top_k_assets: int | None = Field(default=None, ge=2)
    random_seed: int | None = 42
    monte_carlo_samples: int = Field(default=3000, ge=2000)

    @field_validator("preset_name")
    @classmethod
    def validate_preset_name(cls, value):
        if value is None:
            return value
        if value not in DEMO_PRESETS:
            raise ValueError("preset_name must be conservative, balanced, or aggressive")
        return value

    @field_validator("objective_mode")
    @classmethod
    def validate_objective_mode(cls, value):
        if value not in {"sharpe", "risk_adjusted_return"}:
            raise ValueError("objective_mode must be sharpe or risk_adjusted_return")
        return value

    @model_validator(mode="after")
    def validate_weight_constraints(self):
        if (
            self.max_asset_weight is not None
            and self.top_k_assets is not None
            and self.max_asset_weight * self.top_k_assets < 1.0
        ):
            raise ValueError("max_asset_weight * top_k_assets must be at least 1")
        return self
