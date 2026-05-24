"""Request schemas for the FastAPI portfolio optimization API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    particles: int = Field(default=100, ge=20, le=300)
    iterations: int = Field(default=200, ge=50, le=500)
    inertia_weight: float = Field(default=0.7, ge=0.1, le=1.5)
    c1: float = Field(default=1.5, ge=0.5, le=3.0)
    c2: float = Field(default=1.5, ge=0.5, le=3.0)
    risk_free_rate: float = 0.0
    random_seed: int | None = 42
    monte_carlo_samples: int = Field(default=3000, ge=2000)
