# 实验结果数据

本目录由 `python scripts/run_experiments.py` 生成，用于课程报告和答辩分析。

## 文件说明

- `experiment_summary.json`：结构化实验结果，包含元数据、实验结果、随机种子稳定性统计和自动结论。
- `experiment_summary.csv`：扁平化实验结果，便于复制到报告或表格工具。
- `convergence_curves.json`：各实验的 PSO 收敛曲线。

## 数据来源

- data_source: `uci`
- asset_count: `63`
- annualized: `True`
- trading_days_per_year: `None`

如果 `data_source` 不是 `uci`，这些结果只能作为 fallback 演示结果，不能在报告中伪装为真实 UCI 实验。

## 新增实验口径

- 风险偏好预设：保守型使用更强风险厌恶和更严格仓位限制；均衡型最大化 Sharpe Ratio；激进型降低风险惩罚并放宽单项权重上限。
- 单项最大权重约束：对比无上限、50%、25%、15% 等限制，观察集中度和风险收益变化。
- Top-K 入选约束：对比 K=5/10/15/20，将连续权重优化连接到“是否选择资产”的课程要求。
- Monte Carlo baseline 样本数：3000。
- risk_free_rate：0.0。
- 1% 权重阈值只用于解释 `selected_assets`，不改变 PSO 连续权重模型。
