# 实验结果数据

本目录由 `python scripts/run_experiments.py` 生成，用于阶段五 A 的课程实验分析。

## 文件说明

- `experiment_summary.json`：结构化实验结果，包含元数据、各实验组结果和随机种子稳定性统计。
- `experiment_summary.csv`：扁平化实验结果，便于复制到报告或表格工具。
- `convergence_curves.json`：各实验的 PSO 收敛曲线。

## 数据来源

- data_source: `uci`
- asset_count: `63`
- annualized: `True`
- trading_days_per_year: `None`

如果 `data_source` 不是 `uci`，这些结果只能作为 fallback 演示结果，不能在报告中伪装为真实 UCI 实验。

## 实验口径

- PSO 目标函数：最大化 Sharpe Ratio。
- 约束：`wi >= 0` 且 `sum(wi)=1`。
- Monte Carlo baseline 样本数：3000。
- risk_free_rate：0.0。
- 1% 权重阈值只用于解释 `selected_assets`，不参与优化约束。
- 不使用 15% 单票仓位上限。
