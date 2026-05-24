"""Run reproducible Stage 5A PSO experiments for report preparation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, pstdev
import sys
import time

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.data_loader import load_portfolio_dataset
from backend.app.presets import DEMO_PRESETS
from backend.app.pso_optimizer import run_pso
from backend.app.random_baseline import generate_random_portfolios


OUTPUT_DIR = PROJECT_ROOT / "data" / "experiments"
SUMMARY_JSON = OUTPUT_DIR / "experiment_summary.json"
SUMMARY_CSV = OUTPUT_DIR / "experiment_summary.csv"
CURVES_JSON = OUTPUT_DIR / "convergence_curves.json"
README_PATH = OUTPUT_DIR / "README.md"

RISK_FREE_RATE = 0.0
MONTE_CARLO_SAMPLES = 3000
SELECTED_THRESHOLD = 0.01


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = load_portfolio_dataset()
    asset_names = dataset["asset_names"]
    expected_returns = dataset["expected_returns"]
    covariance_matrix = dataset["covariance_matrix"]

    experiments = _build_experiment_specs()
    results = []
    convergence_curves = []

    print(f"data_source: {dataset['data_source']}")
    print(f"asset_count: {len(asset_names)}")
    if dataset["data_source"] != "uci":
        print("warning: experiments are using fallback data, not real UCI data")

    for spec in experiments:
        result, curve = _run_single_experiment(
            spec,
            asset_names,
            expected_returns,
            covariance_matrix,
        )
        results.append(result)
        convergence_curves.append(curve)
        print(
            f"{result['experiment_id']}: sharpe={result['sharpe_ratio']:.6f}, "
            f"mc_best={result['monte_carlo_best_sharpe']:.6f}, "
            f"delta={result['pso_minus_monte_carlo_best_sharpe']:.6f}, "
            f"time={result['compute_time_seconds']:.3f}s"
        )

    seed_stats = _seed_stability_stats(results)
    payload = {
        "metadata": {
            "data_source": dataset["data_source"],
            "asset_count": len(asset_names),
            "annualized": dataset["annualized"],
            "trading_days_per_year": dataset["trading_days_per_year"],
            "risk_free_rate": RISK_FREE_RATE,
            "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            "selected_threshold": SELECTED_THRESHOLD,
            "source_notes": dataset["source_notes"],
        },
        "results": results,
        "seed_stability": seed_stats,
    }

    _write_json(SUMMARY_JSON, payload)
    _write_csv(SUMMARY_CSV, results)
    _write_json(
        CURVES_JSON,
        {
            "metadata": {
                "data_source": dataset["data_source"],
                "asset_count": len(asset_names),
                "note": "Only PSO convergence curves are stored; Monte Carlo scatter points are not stored.",
            },
            "curves": convergence_curves,
        },
    )
    _write_readme(dataset)

    print(f"wrote: {SUMMARY_JSON.relative_to(PROJECT_ROOT)}")
    print(f"wrote: {SUMMARY_CSV.relative_to(PROJECT_ROOT)}")
    print(f"wrote: {CURVES_JSON.relative_to(PROJECT_ROOT)}")
    print(f"wrote: {README_PATH.relative_to(PROJECT_ROOT)}")
    if seed_stats:
        print(
            "seed_stability: "
            f"sharpe_mean={seed_stats['sharpe_ratio_mean']:.6f}, "
            f"sharpe_std={seed_stats['sharpe_ratio_std']:.6f}"
        )


def _build_experiment_specs():
    specs = []

    for preset_name in ("conservative", "balanced", "aggressive"):
        preset = dict(DEMO_PRESETS[preset_name])
        preset["experiment_group"] = "preset_comparison"
        preset["experiment_id"] = f"preset_{preset_name}"
        specs.append(preset)

    for particles in (50, 100, 200):
        specs.append(
            {
                "experiment_group": "particle_count",
                "experiment_id": f"particles_{particles}",
                "preset_name": None,
                "particles": particles,
                "iterations": 200,
                "inertia_weight": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "risk_free_rate": RISK_FREE_RATE,
                "random_seed": 42,
                "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            }
        )

    for iterations in (100, 200, 400):
        specs.append(
            {
                "experiment_group": "iteration_count",
                "experiment_id": f"iterations_{iterations}",
                "preset_name": None,
                "particles": 100,
                "iterations": iterations,
                "inertia_weight": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "risk_free_rate": RISK_FREE_RATE,
                "random_seed": 42,
                "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            }
        )

    for random_seed in (1, 7, 42, 2024, 3407):
        specs.append(
            {
                "experiment_group": "seed_stability",
                "experiment_id": f"seed_{random_seed}",
                "preset_name": None,
                "particles": 100,
                "iterations": 200,
                "inertia_weight": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "risk_free_rate": RISK_FREE_RATE,
                "random_seed": random_seed,
                "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            }
        )

    return specs


def _run_single_experiment(spec, asset_names, expected_returns, covariance_matrix):
    start_time = time.perf_counter()
    pso_result = run_pso(
        expected_returns,
        covariance_matrix,
        particles=spec["particles"],
        iterations=spec["iterations"],
        inertia_weight=spec["inertia_weight"],
        c1=spec["c1"],
        c2=spec["c2"],
        risk_free_rate=spec["risk_free_rate"],
        random_seed=spec["random_seed"],
    )
    baseline_points = generate_random_portfolios(
        expected_returns,
        covariance_matrix,
        samples=spec["monte_carlo_samples"],
        risk_free_rate=spec["risk_free_rate"],
        random_seed=spec["random_seed"],
    )
    compute_time_seconds = time.perf_counter() - start_time

    best_weights = np.asarray(pso_result["best_weights"], dtype=float)
    convergence_curve = pso_result["convergence_curve"]
    convergence_first = float(convergence_curve[0]["sharpe_ratio"])
    convergence_final = float(convergence_curve[-1]["sharpe_ratio"])
    monte_carlo_best_sharpe = max(point["sharpe_ratio"] for point in baseline_points)
    selected_assets_count = int(np.sum(best_weights >= SELECTED_THRESHOLD))

    result = {
        "experiment_group": spec["experiment_group"],
        "experiment_id": spec["experiment_id"],
        "preset_name": spec.get("preset_name"),
        "particles": spec["particles"],
        "iterations": spec["iterations"],
        "inertia_weight": spec["inertia_weight"],
        "c1": spec["c1"],
        "c2": spec["c2"],
        "risk_free_rate": spec["risk_free_rate"],
        "random_seed": spec["random_seed"],
        "monte_carlo_samples": spec["monte_carlo_samples"],
        "expected_return": float(pso_result["expected_return"]),
        "volatility": float(pso_result["volatility"]),
        "sharpe_ratio": float(pso_result["sharpe_ratio"]),
        "selected_assets_count": selected_assets_count,
        "compute_time_seconds": compute_time_seconds,
        "convergence_first": convergence_first,
        "convergence_final": convergence_final,
        "convergence_improvement": convergence_final - convergence_first,
        "best_weights_nonzero_count": int(np.sum(best_weights > 1e-12)),
        "monte_carlo_best_sharpe": float(monte_carlo_best_sharpe),
        "pso_minus_monte_carlo_best_sharpe": float(
            pso_result["sharpe_ratio"] - monte_carlo_best_sharpe
        ),
    }
    curve = {
        "experiment_group": spec["experiment_group"],
        "experiment_id": spec["experiment_id"],
        "preset_name": spec.get("preset_name"),
        "particles": spec["particles"],
        "iterations": spec["iterations"],
        "random_seed": spec["random_seed"],
        "convergence_curve": convergence_curve,
    }
    return result, curve


def _seed_stability_stats(results):
    seed_results = [
        result for result in results if result["experiment_group"] == "seed_stability"
    ]
    if not seed_results:
        return {}

    sharpe_values = [result["sharpe_ratio"] for result in seed_results]
    expected_return_values = [result["expected_return"] for result in seed_results]
    volatility_values = [result["volatility"] for result in seed_results]
    selected_count_values = [result["selected_assets_count"] for result in seed_results]
    return {
        "random_seeds": [result["random_seed"] for result in seed_results],
        "sharpe_ratio_mean": mean(sharpe_values),
        "sharpe_ratio_std": pstdev(sharpe_values),
        "expected_return_mean": mean(expected_return_values),
        "volatility_mean": mean(volatility_values),
        "selected_assets_count_mean": mean(selected_count_values),
    }


def _write_json(path, payload):
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_readme(dataset):
    text = f"""# 实验结果数据

本目录由 `python scripts/run_experiments.py` 生成，用于阶段五 A 的课程实验分析。

## 文件说明

- `experiment_summary.json`：结构化实验结果，包含元数据、各实验组结果和随机种子稳定性统计。
- `experiment_summary.csv`：扁平化实验结果，便于复制到报告或表格工具。
- `convergence_curves.json`：各实验的 PSO 收敛曲线。

## 数据来源

- data_source: `{dataset["data_source"]}`
- asset_count: `{len(dataset["asset_names"])}`
- annualized: `{dataset["annualized"]}`
- trading_days_per_year: `{dataset["trading_days_per_year"]}`

如果 `data_source` 不是 `uci`，这些结果只能作为 fallback 演示结果，不能在报告中伪装为真实 UCI 实验。

## 实验口径

- PSO 目标函数：最大化 Sharpe Ratio。
- 约束：`wi >= 0` 且 `sum(wi)=1`。
- Monte Carlo baseline 样本数：{MONTE_CARLO_SAMPLES}。
- risk_free_rate：{RISK_FREE_RATE}。
- 1% 权重阈值只用于解释 `selected_assets`，不参与优化约束。
- 不使用 15% 单票仓位上限。
"""
    README_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
