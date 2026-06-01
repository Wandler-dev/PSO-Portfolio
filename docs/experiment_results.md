# 实验结果与分析

## 1. 实验目的

本轮实验用于验证三个增强点是否有效：不同风险偏好目标函数、单项最大权重约束、Top-K 入选数量约束。实验仍使用 Monte Carlo 随机组合作为 baseline，用于观察 PSO 结果在风险-收益空间中的相对位置。

## 2. 数据与统一设置

- 数据源：UCI Stock Portfolio Performance。
- `data_source = uci`。
- 候选策略数量：63。
- 每个 UCI ID 被解释为一个候选 stock-selection weighting strategy。
- 权重约束基础形式：`wi >= 0`，`sum(wi) = 1`。
- Monte Carlo baseline 样本数：3000。
- `risk_free_rate = 0.0`。
- 1% 权重阈值只用于解释入选策略，不参与 PSO 搜索。

## 3. 指标说明

本轮实验不只比较收益率和 Sharpe Ratio，还引入了约束和集中度指标，用于解释“收益、风险、选择数量、持仓集中度”之间的权衡。

| 指标 | 含义 | 解读方式 |
|---|---|---|
| `objective_mode` | PSO 实际优化的目标函数类型。`sharpe` 表示最大化 Sharpe Ratio；`risk_adjusted_return` 表示最大化风险厌恶收益。 | 用于解释为什么某些预设收益更高但 Sharpe 不一定最高。 |
| `objective_score` | 当前目标函数下的适应度值。 | 收敛曲线优化的是该值；当目标是 `risk_adjusted_return` 时，它不等同于 Sharpe Ratio。 |
| `risk_aversion` | 风险厌恶系数，出现在 `E(Rp) - Rf - risk_aversion * volatility` 中。 | 数值越大，算法越惩罚波动率；保守型更高，激进型更低。 |
| `expected_return` | 组合期望收益率，来自权重向量与候选策略收益向量的乘积。 | 越高表示收益倾向越强，但必须结合波动率判断。 |
| `volatility` | 组合波动率，计算公式为 `sqrt(w^T Sigma w)`。 | 越低表示风险越低；激进型通常会接受更高波动率。 |
| `sharpe_ratio` | 收益/风险比，计算公式为 `(expected_return - risk_free_rate) / volatility`。 | 衡量单位风险下收益表现，是均衡型的核心评价指标。 |
| `max_asset_weight` | 实验设定的单项最大权重上限。空值表示不设上限。 | 用于控制单个候选策略过度集中。 |
| `actual_max_weight` | PSO 最终组合中的实际最大单项权重。 | 应不超过 `max_asset_weight`；可验证约束是否生效。 |
| `top_k_assets` | 最多允许保留的非零权重候选策略数量。 | 用于贴合课程要求中的“是否选择资产”。 |
| `selected_assets_count` | 权重不低于 1% 的候选策略数量。 | 这是展示解释指标，不是硬约束；但应不超过 `top_k_assets`。 |
| `best_weights_nonzero_count` | 权重大于极小阈值的非零权重数量。 | 用于检查 Top-K 约束是否真的限制了非零权重。 |
| `weight_concentration_hhi` | 权重平方和，类似 Herfindahl-Hirschman Index。 | 越高表示持仓越集中；越低表示组合越分散。 |
| `monte_carlo_best_sharpe` | 同一约束下随机组合 baseline 中最高 Sharpe Ratio。 | 用于衡量 PSO 是否优于随机搜索。 |
| `pso_minus_monte_carlo_best_sharpe` | PSO Sharpe Ratio 减去 Monte Carlo 最佳 Sharpe Ratio。 | 正数表示 PSO 优于随机 baseline；负数表示该配置下 PSO 的 Sharpe 不如随机 baseline 中的最佳样本。 |
| `convergence_metric` | 收敛曲线使用的指标名称。当前统一记录为 `objective_score`。 | 避免将风险厌恶收益目标误读为 Sharpe 收敛。 |
| `convergence_improvement` | 最后一代与第一代 `objective_score` 的差值。 | 用于说明 PSO 迭代是否确实改善了目标函数。 |

需要特别注意：`objective_score` 是 PSO 的搜索目标，`sharpe_ratio` 是投资组合评价指标。两者在 `objective_mode=sharpe` 时相同；在 `objective_mode=risk_adjusted_return` 时不同。因此激进型可以取得更高 `expected_return`，但由于 `volatility` 上升，`sharpe_ratio` 反而较低。

## 4. 风险偏好预设实验

| preset | objective_mode | risk_aversion | max_weight | top_k | expected_return | volatility | sharpe_ratio | selected_count | max_actual_weight |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| conservative | risk_adjusted_return | 2.0 | 0.15 | 10 | 0.1642 | 0.0663 | 2.4772 | 7 | 0.1500 |
| balanced | sharpe | 0.0 | 0.25 | 10 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 |
| aggressive | risk_adjusted_return | 0.2 | 0.50 | 10 | 0.1930 | 0.1035 | 1.8653 | 2 | 0.5000 |

结论：三种预设现在不再只是 PSO 参数强弱，而是代表不同投资偏好。激进型获得最高期望收益率，但波动率明显升高，因此 Sharpe Ratio 不如均衡型；均衡型在收益和风险之间取得更好的收益/风险比；保守型使用更严格仓位限制，组合更分散。

## 5. 单项最大权重约束实验

| experiment | max_weight | expected_return | volatility | sharpe_ratio | selected_count | actual_max_weight | HHI |
|---|---:|---:|---:|---:|---:|---:|---:|
| no cap | - | 0.1583 | 0.0594 | 2.6664 | 2 | 0.6516 | 0.5460 |
| 50% cap | 0.50 | 0.1503 | 0.0558 | 2.6958 | 3 | 0.5000 | 0.3869 |
| 25% cap | 0.25 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| 15% cap | 0.15 | 0.1490 | 0.0572 | 2.6030 | 8 | 0.1500 | 0.1427 |

结论：单项权重上限显著降低组合集中度。无上限时最大权重达到 65.16%，HHI 为 0.5460；加入 15% 上限后最大权重被严格控制为 15%，入选策略数提升到 8，HHI 降至 0.1427。50% 上限在本次结果中 Sharpe Ratio 最高，说明适度限制集中持仓可能降低波动率并改善收益/风险比。

## 6. Top-K 入选约束实验

| experiment | top_k | expected_return | volatility | sharpe_ratio | selected_count | actual_max_weight | HHI |
|---|---:|---:|---:|---:|---:|---:|---:|
| top_k_5 | 5 | 0.1503 | 0.0577 | 2.6062 | 5 | 0.2500 | 0.2287 |
| top_k_10 | 10 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| top_k_15 | 15 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| top_k_20 | 20 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |

结论：Top-K 约束把连续权重优化和课程要求中的“是否选择股票/资产”连接起来。K=5 时组合最紧凑，仍能达到 2.6062 的 Sharpe Ratio；K 增大到 10 后达到 2.6076，继续增大 K 没有显著提升，说明有效组合主要由少数候选策略构成。

## 7. 随机种子稳定性

固定 `max_asset_weight=0.25`、`top_k_assets=10`、目标函数为最大化 Sharpe Ratio，改变随机种子：

- `sharpe_ratio_mean = 2.6873`
- `sharpe_ratio_std = 0.0405`

结论：不同随机种子下 Sharpe Ratio 有一定波动，但整体保持在较高水平。PSO 是启发式搜索算法，不保证数学全局最优，因此报告中应说明随机初始化会影响最终结果。

## 8. 总体结论

增强后的实验更能体现工作量和课程要求：

- 风险偏好目标让保守、均衡、激进三种模式有真实含义。
- 单项最大权重约束解决了原始结果中权重过度集中问题。
- Top-K 约束体现了“是否选择资产”的离散解释。
- PSO 在多数实验组中仍优于对应 Monte Carlo 随机组合的最佳 Sharpe Ratio。

需要注意的是，UCI 数据不是原始股票价格序列，本项目优化的是候选策略之间的资金分配权重；实验结论应定位为课程建模和算法演示结果，而不是实际投资建议。
