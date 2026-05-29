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

from backend.app.data_loader import load_portfolio_dataset  # noqa: E402
from backend.app.presets import DEMO_PRESETS  # noqa: E402
from backend.app.pso_optimizer import run_pso  # noqa: E402
from backend.app.random_baseline import generate_random_portfolios  # noqa: E402


OUTPUT_DIR = PROJECT_ROOT / "data" / "experiments"
SUMMARY_JSON = OUTPUT_DIR / "experiment_summary.json"
SUMMARY_CSV = OUTPUT_DIR / "experiment_summary.csv"
CURVES_JSON = OUTPUT_DIR / "convergence_curves.json"
README_PATH = OUTPUT_DIR / "README.md"

RISK_FREE_RATE = 0.0
MONTE_CARLO_SAMPLES = 3000
SELECTED_THRESHOLD = 0.01
DEFAULT_OBJECTIVE_MODE = "sharpe"
DEFAULT_RISK_AVERSION = 0.0
DEFAULT_MAX_ASSET_WEIGHT = 0.25
DEFAULT_TOP_K_ASSETS = 10


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
    conclusions = _build_conclusions(results)
    payload = {
        "metadata": {
            "data_source": dataset["data_source"],
            "asset_count": len(asset_names),
            "annualized": dataset["annualized"],
            "trading_days_per_year": dataset["trading_days_per_year"],
            "risk_free_rate": RISK_FREE_RATE,
            "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            "selected_threshold": SELECTED_THRESHOLD,
            "default_max_asset_weight": DEFAULT_MAX_ASSET_WEIGHT,
            "default_top_k_assets": DEFAULT_TOP_K_ASSETS,
            "source_notes": dataset["source_notes"],
        },
        "results": results,
        "seed_stability": seed_stats,
        "conclusions": conclusions,
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
        preset["experiment_group"] = "risk_preference_preset"
        preset["experiment_id"] = f"preset_{preset_name}"
        specs.append(preset)

    for max_asset_weight in (None, 0.50, 0.25, 0.15):
        specs.append(
            {
                "experiment_group": "max_weight_constraint",
                "experiment_id": (
                    "max_weight_none"
                    if max_asset_weight is None
                    else f"max_weight_{int(max_asset_weight * 100)}pct"
                ),
                "preset_name": None,
                "particles": 100,
                "iterations": 200,
                "inertia_weight": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "risk_free_rate": RISK_FREE_RATE,
                "objective_mode": DEFAULT_OBJECTIVE_MODE,
                "risk_aversion": DEFAULT_RISK_AVERSION,
                "max_asset_weight": max_asset_weight,
                "top_k_assets": DEFAULT_TOP_K_ASSETS,
                "random_seed": 42,
                "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            }
        )

    for top_k_assets in (5, 10, 15, 20):
        specs.append(
            {
                "experiment_group": "top_k_selection",
                "experiment_id": f"top_k_{top_k_assets}",
                "preset_name": None,
                "particles": 100,
                "iterations": 200,
                "inertia_weight": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "risk_free_rate": RISK_FREE_RATE,
                "objective_mode": DEFAULT_OBJECTIVE_MODE,
                "risk_aversion": DEFAULT_RISK_AVERSION,
                "max_asset_weight": DEFAULT_MAX_ASSET_WEIGHT,
                "top_k_assets": top_k_assets,
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
                "objective_mode": DEFAULT_OBJECTIVE_MODE,
                "risk_aversion": DEFAULT_RISK_AVERSION,
                "max_asset_weight": DEFAULT_MAX_ASSET_WEIGHT,
                "top_k_assets": DEFAULT_TOP_K_ASSETS,
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
        objective_mode=spec["objective_mode"],
        risk_aversion=spec["risk_aversion"],
        max_asset_weight=spec["max_asset_weight"],
        top_k_assets=spec["top_k_assets"],
    )
    baseline_points = generate_random_portfolios(
        expected_returns,
        covariance_matrix,
        samples=spec["monte_carlo_samples"],
        risk_free_rate=spec["risk_free_rate"],
        random_seed=spec["random_seed"],
        max_asset_weight=spec["max_asset_weight"],
        top_k_assets=spec["top_k_assets"],
    )
    compute_time_seconds = time.perf_counter() - start_time

    best_weights = np.asarray(pso_result["best_weights"], dtype=float)
    convergence_curve = pso_result["convergence_curve"]
    convergence_metric = "objective_score"
    convergence_first = float(convergence_curve[0][convergence_metric])
    convergence_final = float(convergence_curve[-1][convergence_metric])
    monte_carlo_best_sharpe = max(point["sharpe_ratio"] for point in baseline_points)
    selected_assets_count = int(np.sum(best_weights >= SELECTED_THRESHOLD))
    max_weight = float(np.max(best_weights))
    weight_concentration_hhi = float(np.sum(best_weights ** 2))

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
        "objective_mode": spec["objective_mode"],
        "risk_aversion": spec["risk_aversion"],
        "max_asset_weight": spec["max_asset_weight"],
        "top_k_assets": spec["top_k_assets"],
        "random_seed": spec["random_seed"],
        "monte_carlo_samples": spec["monte_carlo_samples"],
        "objective_score": float(pso_result["objective_score"]),
        "expected_return": float(pso_result["expected_return"]),
        "volatility": float(pso_result["volatility"]),
        "sharpe_ratio": float(pso_result["sharpe_ratio"]),
        "selected_assets_count": selected_assets_count,
        "actual_max_weight": max_weight,
        "weight_concentration_hhi": weight_concentration_hhi,
        "compute_time_seconds": compute_time_seconds,
        "convergence_metric": convergence_metric,
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
        "objective_mode": spec["objective_mode"],
        "max_asset_weight": spec["max_asset_weight"],
        "top_k_assets": spec["top_k_assets"],
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


def _build_conclusions(results):
    conclusions = []

    preset_results = _results_by_group(results, "risk_preference_preset")
    if preset_results:
        ordered = {
            result["preset_name"]: result
            for result in preset_results
            if result["preset_name"] is not None
        }
        conservative = ordered.get("conservative")
        balanced = ordered.get("balanced")
        aggressive = ordered.get("aggressive")
        if conservative and balanced and aggressive:
            conclusions.append(
                {
                    "topic": "risk_preference",
                    "finding": (
                        "Risk preference presets now optimize different objective/constraint "
                        "settings: conservative uses stronger risk aversion and tighter "
                        "position limits, aggressive uses weaker risk aversion and looser "
                        "limits, while balanced maximizes Sharpe ratio."
                    ),
                    "evidence": {
                        "conservative": _brief_result(conservative),
                        "balanced": _brief_result(balanced),
                        "aggressive": _brief_result(aggressive),
                    },
                }
            )

    max_weight_results = _results_by_group(results, "max_weight_constraint")
    if max_weight_results:
        unconstrained = next(
            (result for result in max_weight_results if result["max_asset_weight"] is None),
            None,
        )
        tightest = min(
            (
                result
                for result in max_weight_results
                if result["max_asset_weight"] is not None
            ),
            key=lambda item: item["max_asset_weight"],
            default=None,
        )
        if unconstrained and tightest:
            conclusions.append(
                {
                    "topic": "max_weight_constraint",
                    "finding": (
                        "A single-asset weight cap reduces concentration. The trade-off can "
                        "be read from Sharpe ratio, volatility, selected asset count, and HHI."
                    ),
                    "evidence": {
                        "unconstrained": _brief_result(unconstrained),
                        "tightest_constraint": _brief_result(tightest),
                    },
                }
            )

    top_k_results = _results_by_group(results, "top_k_selection")
    if top_k_results:
        best_by_sharpe = max(top_k_results, key=lambda item: item["sharpe_ratio"])
        sparsest = min(top_k_results, key=lambda item: item["top_k_assets"])
        conclusions.append(
            {
                "topic": "top_k_selection",
                "finding": (
                    "Top-K constraints connect continuous weights to the course requirement "
                    "of selecting assets. Smaller K gives a more compact portfolio, while "
                    "larger K allows more diversification."
                ),
                "evidence": {
                    "best_top_k_by_sharpe": _brief_result(best_by_sharpe),
                    "sparsest_top_k": _brief_result(sparsest),
                },
            }
        )

    return conclusions


def _results_by_group(results, group_name):
    return [result for result in results if result["experiment_group"] == group_name]


def _brief_result(result):
    return {
        "experiment_id": result["experiment_id"],
        "expected_return": result["expected_return"],
        "volatility": result["volatility"],
        "sharpe_ratio": result["sharpe_ratio"],
        "selected_assets_count": result["selected_assets_count"],
        "actual_max_weight": result["actual_max_weight"],
        "weight_concentration_hhi": result["weight_concentration_hhi"],
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

本目录由 `python scripts/run_experiments.py` 生成，用于课程报告和答辩分析。

## 文件说明

- `experiment_summary.json`：结构化实验结果，包含元数据、实验结果、随机种子稳定性统计和自动结论。
- `experiment_summary.csv`：扁平化实验结果，便于复制到报告或表格工具。
- `convergence_curves.json`：各实验的 PSO 收敛曲线。

## 数据来源

- data_source: `{dataset["data_source"]}`
- asset_count: `{len(dataset["asset_names"])}`
- annualized: `{dataset["annualized"]}`
- trading_days_per_year: `{dataset["trading_days_per_year"]}`

如果 `data_source` 不是 `uci`，这些结果只能作为 fallback 演示结果，不能在报告中伪装为真实 UCI 实验。

## 新增实验口径

- 风险偏好预设：保守型使用更强风险厌恶和更严格仓位限制；均衡型最大化 Sharpe Ratio；激进型降低风险惩罚并放宽单项权重上限。
- 单项最大权重约束：对比无上限、50%、25%、15% 等限制，观察集中度和风险收益变化。
- Top-K 入选约束：对比 K=5/10/15/20，将连续权重优化连接到“是否选择资产”的课程要求。
- Monte Carlo baseline 样本数：{MONTE_CARLO_SAMPLES}。
- risk_free_rate：{RISK_FREE_RATE}。
- 1% 权重阈值只用于解释 `selected_assets`，不改变 PSO 连续权重模型。
"""
    README_PATH.write_text(text, encoding="utf-8")
    return
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
