"""FastAPI app for the portfolio PSO backend."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.schemas import OptimizeRequest
from backend.app.services import build_data_summary, run_optimization_service


app = FastAPI(title="portfolio-pso-backend")


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "portfolio-pso-backend",
        "data_source_ready": True,
    }


@app.get("/api/data/summary")
def data_summary():
    return build_data_summary()


@app.post("/api/optimize")
def optimize(request: OptimizeRequest):
    return run_optimization_service(request)
