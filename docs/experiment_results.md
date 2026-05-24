# 实验结果与分析

## 1. 实验目的

本阶段实验用于验证 PSO 是否能在 UCI 候选策略权重空间中找到较高 Sharpe Ratio 的组合，并观察不同 PSO 参数对收敛效果和运行时间的影响。实验同时使用 Monte Carlo 随机组合 baseline 作为对照，用于判断 PSO 结果在随机组合分布中的相对位置。

需要强调的是，Monte Carlo baseline 是随机组合基准，不是理论全局最优；PSO 也是启发式算法，本实验只能说明其在当前数据和参数设置下找到了较高 Sharpe Ratio 的近似最优组合。

## 2. 数据说明

实验使用 UCI Stock Portfolio Performance 数据集。该数据不是 `date/symbol/close` 股票价格表，而是 weighted scoring stock portfolios 的表现数据。本项目将每个 UCI ID 解释为一个候选 stock-selection weighting strategy，PSO 优化的是这些候选策略之间的资金分配权重。

本次实验的数据加载结果如下：

- `data_source`: `uci`
- 候选策略数量：63
- `expected_returns` 来自 `all period` sheet 的 `original_Annual Return` 字段。
- `covariance_matrix` 由 `1st period`、`2nd period`、`3rd period`、`4th period` 的 Annual Return observations 构造。
- UCI Annual Return 已是表现指标，不使用 252 日年化。
- 协方差矩阵只基于 4 个 period observations 估计，存在低秩和估计不稳定的局限。

## 3. 实验设置

- PSO 目标函数：最大化 `Sharpe Ratio = (E(Rp) - Rf) / volatility`。
- 组合波动率：`volatility = sqrt(w^T Sigma w)`。
- 约束条件：`wi >= 0` 且 `sum(wi)=1`。
- 1% 阈值只用于解释 `selected_assets`，不参与 PSO 优化搜索。
- Monte Carlo baseline 样本数：3000。
- `risk_free_rate = 0.0`。
- 不使用 15% 单票仓位上限。

## 4. Preset 对比结果

| preset_name | particles | iterations | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| conservative | 50 | 150 | 0.1466 | 0.0546 | 2.6861 | 5 | 0.274 | 1.8743 | 0.8118 |
| balanced | 100 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.546 | 1.8743 | 0.9869 |
| aggressive | 200 | 400 | 0.1342 | 0.0469 | 2.8611 | 2 | 1.941 | 1.8743 | 0.9869 |

`balanced` 和 `aggressive` 在本次实验中达到相同 Sharpe Ratio，均高于 `conservative`。`aggressive` 的计算时间明显增加，但没有带来额外提升，说明在当前数据和参数下，继续增加粒子数和迭代数出现边际收益递减。

## 5. 粒子数量影响

固定 `iterations=200`、`inertia_weight=0.7`、`c1=1.5`、`c2=1.5`、`random_seed=42`，改变粒子数量：

| particles | iterations | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 200 | 0.1452 | 0.0536 | 2.7083 | 2 | 0.327 | 1.8743 | 0.8340 |
| 100 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.527 | 1.8743 | 0.9869 |
| 200 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.934 | 1.8743 | 0.9869 |

粒子数从 50 增加到 100 时，Sharpe Ratio 从 2.7083 提升到 2.8611；继续增加到 200 后没有进一步提升，但运行时间继续增加。因此，粒子数增加有助于增强搜索覆盖，但在本实验中 100 个粒子后边际收益明显递减。

## 6. 迭代次数影响

固定 `particles=100`、`inertia_weight=0.7`、`c1=1.5`、`c2=1.5`、`random_seed=42`，改变迭代次数：

| iterations | particles | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.317 | 1.8743 | 0.9869 |
| 200 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.511 | 1.8743 | 0.9869 |
| 400 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.958 | 1.8743 | 0.9869 |

在本数据和随机种子下，100 次迭代已经达到后续 200、400 次迭代相同的最终 Sharpe Ratio。收敛曲线后段趋于平台，说明继续增加迭代次数主要增加计算时间，并未改善最终结果。

## 7. 随机种子稳定性

固定 `particles=100`、`iterations=200`、`inertia_weight=0.7`、`c1=1.5`、`c2=1.5`，改变随机种子：

| random_seed | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.515 | 1.8803 | 0.9808 |
| 7 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.514 | 1.8736 | 0.9875 |
| 42 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.516 | 1.8743 | 0.9869 |
| 2024 | 0.1371 | 0.0484 | 2.8347 | 2 | 0.500 | 1.8812 | 0.9535 |
| 3407 | 0.1452 | 0.0536 | 2.7083 | 2 | 0.518 | 1.8775 | 0.8308 |

随机种子统计：

- `sharpe_ratio_mean = 2.8253`
- `sharpe_ratio_std = 0.0594`
- `expected_return_mean = 0.1370`
- `volatility_mean = 0.0485`
- `selected_assets_count_mean = 2.0`

大多数随机种子得到接近的结果，其中 seed 3407 的 Sharpe Ratio 较低，说明 PSO 结果存在一定随机性。总体看，固定参数下结果较稳定，但仍应在报告中说明 PSO 是启发式搜索，受初始化和随机过程影响。

## 8. 结论

PSO 在当前 UCI 数据解释方式和参数设置下，可以找到较高 Sharpe Ratio 的近似最优组合。相比 Monte Carlo 随机组合 baseline，PSO 提供了更有方向的搜索过程；在所有实验组中，PSO 的 Sharpe Ratio 均高于对应随机组合 baseline 的最佳 Sharpe Ratio。

但 PSO 是启发式算法，不保证数学意义上的全局最优。UCI 数据也不是原始股票价格表，本项目将每个 ID 解释为候选策略，因此实验结论应理解为“候选策略组合权重优化”的课程建模结果。同时，协方差矩阵基于有限 period observations 构造，存在低秩和估计不稳定的局限。
