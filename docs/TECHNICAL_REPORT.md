# 基于粒子群优化算法的投资组合风险-收益均衡决策系统技术报告

## 1. 项目概述

本项目实现了一个基于粒子群优化算法（Particle Swarm Optimization, PSO）的投资组合风险-收益均衡决策系统。系统面向课程项目场景，用于展示如何将投资组合优化问题建模为连续权重优化问题，并通过手写 PSO 算法搜索候选策略之间的资金分配权重。

系统由 Python 后端、FastAPI 接口、Vue 3 + ECharts 前端界面和实验脚本组成。项目不是实盘交易系统，不接入券商接口，不执行自动下单，也不提供投资建议。

## 2. 数据集与建模解释

项目使用 UCI Stock Portfolio Performance 数据集，原始文件位于：

```text
data/raw/stock portfolio performance data set.xlsx
```

该数据集不是 `date / symbol / close` 格式的股票价格时间序列，而是 weighted scoring stock portfolios 的表现数据。每个 UCI ID 可理解为一种基于选股概念权重构造的候选 stock-selection weighting strategy。

因此，本项目将 63 个有效 ID 建模为 63 个候选投资策略，记为 `Strategy_1` 到 `Strategy_63`。PSO 优化的是这些候选策略之间的资金分配权重，而不是直接优化单只股票的日度价格序列。

当前数据解析口径如下：

- `expected_returns` 来自 `all period` sheet 的 `original Annual Return`。
- `covariance_matrix` 由 `1st period`、`2nd period`、`3rd period`、`4th period` 的 Annual Return observations 按 ID 对齐后构造。
- UCI 的 Annual Return 已经是绩效指标，不再进行 252 个交易日年化。
- 如果 UCI 文件不存在或解析失败，系统会使用 `simulated_fallback`，并在 API 响应中明确标注。

该建模存在边界：协方差矩阵只基于 4 个 period observations 估计，样本期数较少，存在低秩和估计不稳定问题。因此实验结果应理解为课程建模与算法展示结果，而不是实际市场投资结论。

## 3. 投资组合优化模型

设候选策略数量为 `N`，本项目中 `N = 63`。优化变量为连续权重向量：

```text
w = [w1, w2, ..., wN]
```

基础约束为：

```text
wi >= 0
sum(wi) = 1
```

组合期望收益：

```text
E(Rp) = w^T mu
```

组合波动率：

```text
volatility = sqrt(w^T Sigma w)
```

其中 `mu` 为候选策略期望收益向量，`Sigma` 为候选策略收益协方差矩阵。

系统支持两类目标函数：

1. 最大化夏普比率（Sharpe Ratio）：

```text
Sharpe Ratio = (E(Rp) - Rf) / volatility
```

2. 风险厌恶收益目标：

```text
objective_score = E(Rp) - Rf - risk_aversion * volatility
```

当前实验中 `Rf = 0.0`。`objective_score` 是 PSO 实际优化的适应度值；当 `objective_mode = sharpe` 时，`objective_score` 等同于 Sharpe Ratio；当 `objective_mode = risk_adjusted_return` 时，`objective_score` 不等同于 Sharpe Ratio。

系统还支持两个可选约束：

- `max_asset_weight`：单个候选策略的最大权重上限。
- `top_k_assets`：最多保留的非零权重候选策略数量。

优化结果展示中使用 1% 权重阈值解释入选策略：

```text
wi >= 0.01 -> selected_assets
```

该阈值只用于结果解释和界面展示，不改变 PSO 连续权重搜索过程。

## 4. PSO 算法实现

PSO 通过粒子群在搜索空间中迭代移动，利用个体最优和群体最优引导搜索。本项目中，每个粒子的位置表示一组 63 维投资组合权重，粒子速度表示权重更新方向。

核心流程如下：

```text
1. 随机初始化粒子位置和速度。
2. 对每个粒子位置执行约束处理：
   - 非负化；
   - Top-K 筛选；
   - 单项最大权重限制；
   - 权重归一化。
3. 计算每个粒子的 objective_score。
4. 初始化每个粒子的个体最优 pBest 和群体全局最优 gBest。
5. 对 iteration = 1 ... max_iterations:
   5.1 根据惯性项、个体学习项、群体学习项更新速度。
   5.2 根据速度更新粒子位置。
   5.3 再次执行约束处理。
   5.4 重新计算 objective_score。
   5.5 更新 pBest 和 gBest。
   5.6 记录 convergence_curve。
6. 输出 best_weights、expected_return、volatility、sharpe_ratio、objective_score。
```

项目中的 PSO 核心算法手写实现，不使用 `scipy.optimize`、`pyswarms` 或其他黑盒优化库。

## 5. 系统实现

后端主要模块：

- `backend/app/data_loader.py`：读取 UCI Excel，构造 `expected_returns` 和 `covariance_matrix`，提供 fallback 数据。
- `backend/app/portfolio_math.py`：实现权重归一化、收益、波动率和 Sharpe Ratio 计算。
- `backend/app/pso_optimizer.py`：实现手写 PSO 和约束处理。
- `backend/app/random_baseline.py`：生成 Monte Carlo 随机组合 baseline。
- `backend/app/services.py`：串联数据加载、PSO、随机 baseline 和响应组装。
- `backend/app/main.py`：FastAPI 应用入口。

主要 API：

- `GET /api/health`：检查后端服务状态。
- `GET /api/data/summary`：返回数据源摘要。
- `GET /api/presets`：返回 conservative、balanced、aggressive 三组预设。
- `POST /api/optimize`：运行优化并返回 KPI、最优权重、收敛曲线、风险-收益散点数据和入选策略表。

前端使用 Vue 3、Element Plus 和 ECharts，实现：

- 参数控制面板；
- KPI 指标卡片；
- PSO 收敛曲线；
- 最优组合权重 Top 10；
- 风险-收益散点图；
- 入选策略表；
- 三组 preset 的指标对比和权重对比。

系统还提供本地缓存。`cache_hit` 只表示命中相同参数的历史计算结果，不改变算法定义或实验真实性。

## 6. 实验设计

实验脚本为：

```bash
python scripts/run_experiments.py
```

实验结果输出到：

```text
data/experiments/experiment_summary.json
data/experiments/experiment_summary.csv
data/experiments/convergence_curves.json
```

统一设置：

- 数据源：UCI Stock Portfolio Performance。
- 候选策略数量：63。
- `risk_free_rate = 0.0`。
- Monte Carlo baseline 样本数：3000。
- 1% 权重阈值只用于解释入选策略。

实验组包括：

1. 风险偏好预设实验：比较 conservative、balanced、aggressive。
2. 单项最大权重约束实验：比较无上限、50%、25%、15%。
3. Top-K 入选约束实验：比较 K=5、10、15、20。
4. 随机种子稳定性实验：比较多个 random_seed。

Monte Carlo baseline 是随机组合基准，不是理论全局最优。PSO 结果也应表述为当前参数和数据下的近似最优组合。

## 7. 实验结果与分析

### 7.1 风险偏好预设实验

| preset | objective_mode | risk_aversion | max_weight | top_k | expected_return | volatility | sharpe_ratio | selected_count | max_actual_weight |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| conservative | risk_adjusted_return | 2.0 | 0.15 | 10 | 0.1642 | 0.0663 | 2.4772 | 7 | 0.1500 |
| balanced | sharpe | 0.0 | 0.25 | 10 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 |
| aggressive | risk_adjusted_return | 0.2 | 0.50 | 10 | 0.1930 | 0.1035 | 1.8653 | 2 | 0.5000 |

三种预设对应不同风险偏好。激进型获得最高期望收益率，但波动率显著升高，因此 Sharpe Ratio 不如均衡型；均衡型在收益和风险之间取得更好的收益/风险比；保守型通过更严格仓位限制降低集中度。

### 7.2 单项最大权重约束实验

| experiment | max_weight | expected_return | volatility | sharpe_ratio | selected_count | actual_max_weight | HHI |
|---|---:|---:|---:|---:|---:|---:|---:|
| no cap | - | 0.1583 | 0.0594 | 2.6664 | 2 | 0.6516 | 0.5460 |
| 50% cap | 0.50 | 0.1503 | 0.0558 | 2.6958 | 3 | 0.5000 | 0.3869 |
| 25% cap | 0.25 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| 15% cap | 0.15 | 0.1490 | 0.0572 | 2.6030 | 8 | 0.1500 | 0.1427 |

单项权重上限显著降低组合集中度。无上限时最大权重达到 65.16%，HHI 为 0.5460；15% 上限将最大权重控制为 15%，入选策略数提升到 8，HHI 降至 0.1427。

### 7.3 Top-K 入选约束实验

| experiment | top_k | expected_return | volatility | sharpe_ratio | selected_count | actual_max_weight | HHI |
|---|---:|---:|---:|---:|---:|---:|---:|
| top_k_5 | 5 | 0.1503 | 0.0577 | 2.6062 | 5 | 0.2500 | 0.2287 |
| top_k_10 | 10 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| top_k_15 | 15 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |
| top_k_20 | 20 | 0.1517 | 0.0582 | 2.6076 | 5 | 0.2500 | 0.2190 |

Top-K 约束将连续权重优化和“是否选择资产”的解释连接起来。K=5 时组合最紧凑，仍能达到 2.6062 的 Sharpe Ratio；K 增大到 10 后略有提升，继续增大 K 没有明显收益。

### 7.4 随机种子稳定性

固定 `max_asset_weight=0.25`、`top_k_assets=10`，目标函数为最大化 Sharpe Ratio：

- `sharpe_ratio_mean = 2.6873`
- `sharpe_ratio_std = 0.0405`

结果说明 PSO 对随机初始化存在一定敏感性，但整体保持较高 Sharpe Ratio。由于 PSO 是启发式算法，不能声称保证全局最优。

## 8. 运行与复现

创建环境：

```bash
conda env create -f environment.yml
conda activate portfolio-pso
```

启动系统：

```bash
make demo
```

测试后端：

```bash
pytest
python scripts/smoke_api.py
```

构建前端：

```bash
cd frontend
npm install
npm run build
```

复现实验：

```bash
python scripts/run_experiments.py
```

## 9. 总结与局限

本项目完成了从数据加载、优化建模、手写 PSO、API 封装、Web 可视化到实验分析的完整闭环。实验结果表明，PSO 能在当前 UCI 候选策略权重空间中搜索到风险-收益表现较好的组合，并且可以通过风险偏好、单项权重上限和 Top-K 约束展示不同组合结构的变化。

主要局限：

- UCI 数据不是原始股票价格时间序列。
- 协方差矩阵基于有限 period observations，稳定性有限。
- PSO 是启发式算法，不保证全局最优。
- 当前系统未考虑交易成本、调仓频率、行业约束和流动性约束。
- 系统不提供投资建议，不应用于实盘交易。
