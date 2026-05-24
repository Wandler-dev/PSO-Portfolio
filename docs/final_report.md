# 基于粒子群优化算法的投资组合风险-收益均衡决策系统

## 1. 项目背景与问题定义

投资组合优化是金融工程与智能优化中的典型问题。其核心目标是在有限资金约束下，对多个可投资对象分配资金权重，使组合在收益和风险之间取得较好的平衡。本课程项目围绕投资组合优化问题，使用粒子群优化算法（Particle Swarm Optimization, PSO）搜索候选策略权重分配方案，并通过 Web 可视化界面展示优化结果。

本项目的优化目标是最大化 Sharpe Ratio。Sharpe Ratio 同时考虑组合期望收益、无风险收益率和组合波动率，适合用于衡量单位波动率下的收益表现。系统输入为候选投资策略的期望收益向量和协方差矩阵，输出为一组满足约束的连续权重向量。

本系统不是股票自动交易系统，不接入券商接口，不执行实盘下单，也不提供投资建议。项目定位是“智能算法与应用”课程中的投资组合优化实验系统，重点在于数学建模、手写 PSO 求解、实验对比和结果可视化。

## 2. 数据集说明

项目使用 UCI Stock Portfolio Performance 数据集。该数据集不是 `date / symbol / close` 格式的股票价格时间序列，而是 weighted scoring stock portfolios 的表现数据。数据中的每个 ID 对应一种基于选股概念权重构造的 stock-selection weighting strategy。

因此，本项目没有将每一行解释为单只股票，也没有使用日度价格数据计算日收益率。数据加载器将 63 个有效 ID 解释为 63 个候选投资策略，记为 `Strategy_1` 到 `Strategy_63`。PSO 优化的是这些候选策略之间的资金分配权重。

在当前数据解析中：

- `expected_returns` 来自 `all period` sheet 的 `original_Annual Return` 字段。
- `covariance_matrix` 由 `1st period`、`2nd period`、`3rd period`、`4th period` 的 Annual Return observations 构造。
- UCI 的 Annual Return 已经是 performance-level 指标，因此不进行 252 日年化。
- `data_source = uci`。
- 有效候选策略数量 `N = 63`。

该数据处理方式存在局限。协方差矩阵仅基于 4 个 period observations 估计，样本期数较少，矩阵存在低秩和估计不稳定问题。因此实验结果应理解为课程建模下的优化结果，而不是对真实市场投资收益的保证。

## 3. 投资组合优化建模

设候选策略数量为 `N`，本项目中 `N = 63`。优化变量为连续权重向量：

```text
w = [w1, w2, ..., wN]
```

其中 `wi` 表示第 `i` 个候选策略的资金分配比例。

约束条件为：

```text
wi >= 0
sum(wi) = 1
```

该约束表示不允许卖空，并且资金全部分配到候选策略集合中。

设 `mu` 为候选策略期望收益向量，`Sigma` 为候选策略收益协方差矩阵。组合期望收益为：

```text
E(Rp) = w^T mu
```

组合波动率为：

```text
volatility = sqrt(w^T Sigma w)
```

目标函数为最大化 Sharpe Ratio：

```text
maximize Sharpe Ratio = (E(Rp) - Rf) / volatility
```

当前实验中 `Rf = 0.0`。系统对外字段统一使用 `expected_return`、`volatility` 和 `sharpe_ratio`。

优化完成后，系统使用 1% 权重阈值解释入选策略：

```text
wi >= 0.01 -> selected_assets
wi < 0.01  -> 未实质入选
```

该阈值只用于结果解释和界面展示，不参与 PSO 搜索约束，也不改变连续权重优化模型。

## 4. PSO 算法设计

PSO 是一种群体智能优化算法。算法通过多个粒子在搜索空间中移动，利用个体历史最优位置和群体全局最优位置引导搜索方向。本项目中，每个粒子的位置表示一组 63 维投资组合权重向量，粒子速度表示权重向量的更新方向。

每个粒子维护：

- 当前粒子位置 `x_i`：一组候选策略权重。
- 当前粒子速度 `v_i`：位置更新方向。
- 个体最优 `pBest_i`：该粒子历史上 Sharpe Ratio 最高的位置。

群体维护：

- 全局最优 `gBest`：所有粒子历史上 Sharpe Ratio 最高的位置。

算法步骤如下：

```text
1. 初始化粒子位置 x_i 和速度 v_i
2. 对每个 x_i 执行非负处理和归一化，使其满足 wi >= 0 且 sum(wi)=1
3. 计算每个粒子的 Sharpe Ratio
4. 初始化 pBest_i 和 gBest
5. 对 iteration = 1 ... max_iterations:
   5.1 根据惯性项、个体学习项和群体学习项更新速度 v_i
   5.2 根据速度更新位置 x_i
   5.3 对 x_i 执行非负处理和归一化
   5.4 重新计算 Sharpe Ratio
   5.5 更新 pBest_i
   5.6 更新 gBest
   5.7 记录当前 gBest 的 Sharpe Ratio 到 convergence_curve
6. 输出 gBest 对应的 best_weights、expected_return、volatility 和 sharpe_ratio
```

位置更新后可能出现负权重或权重和不为 1，因此项目在每轮更新后执行约束处理：先将负值截断为 0，再进行归一化；如果权重和为 0，则使用均匀权重兜底。这样可以保证进入目标函数计算的每个组合满足非负和归一化约束。

PSO 是启发式算法，不保证数学意义上的全局最优。但对于本项目的高维连续权重搜索问题，PSO 具有实现直观、参数可控、收敛过程可记录等优点。

## 5. 系统设计与实现

系统由后端算法模块、FastAPI 服务、前端 Web 可视化界面和实验脚本组成。

后端主要模块如下：

- `backend/app/data_loader.py`：解析 UCI Excel 数据，构造 `expected_returns` 和 `covariance_matrix`；如果数据不存在或解析失败，则返回明确标记的 fallback 数据。
- `backend/app/portfolio_math.py`：实现权重归一化、组合期望收益、组合波动率和 Sharpe Ratio 计算。
- `backend/app/pso_optimizer.py`：实现手写 PSO 优化过程，输出最优权重和收敛曲线。
- `backend/app/random_baseline.py`：生成 Monte Carlo 随机组合 baseline，用于风险-收益散点对比。
- `backend/app/services.py`：封装数据加载、PSO 优化、随机 baseline 和响应组装流程。

FastAPI 后端提供以下接口：

- `GET /api/health`：检查服务状态。
- `GET /api/data/summary`：返回数据源、候选策略数量和数据说明。
- `GET /api/presets`：返回 `conservative`、`balanced`、`aggressive` 三组预设参数。
- `POST /api/optimize`：运行优化并返回 KPI、收敛曲线、随机组合点、最优点和权重表。

系统还实现了 presets 和本地缓存机制。缓存只保存相同数据和相同参数下已经计算过的完整优化响应，用于提高本地系统响应速度。`cache_hit` 表示工程缓存命中，不改变 PSO 算法、目标函数或约束，也不改变结果来源。

前端使用 Vue 3、Element Plus 和 ECharts。Web 可视化界面包含参数控制、KPI 指标、PSO 收敛曲线、Top 10 权重图、风险-收益散点图和入选策略表。前端不依赖 CDN，所有依赖均通过本地 npm 管理。

## 6. 实验设计

实验基于 UCI 数据加载结果运行，固定设置如下：

- `risk_free_rate = 0.0`
- Monte Carlo baseline 样本数为 3000
- 1% 权重阈值只用于统计 `selected_assets_count`
- 不使用 15% 单票仓位上限
- 不使用黑盒优化库

实验分为四组：

1. Preset 对比：比较 `conservative`、`balanced`、`aggressive` 三组预设参数。
2. 粒子数量对比：固定其他参数，比较 `particles = 50, 100, 200`。
3. 迭代次数对比：固定其他参数，比较 `iterations = 100, 200, 400`。
4. 随机种子稳定性：固定 PSO 参数，比较 `random_seed = 1, 7, 42, 2024, 3407`。

每次实验都生成 3000 个 Monte Carlo 随机组合，并记录随机组合中的最高 Sharpe Ratio。Monte Carlo baseline 是随机组合基准，不是理论最优解；PSO 结果也应表述为当前实验设置下的近似最优组合。

## 7. 实验结果与分析

### 7.1 Preset 对比

| preset_name | particles | iterations | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| conservative | 50 | 150 | 0.1466 | 0.0546 | 2.6861 | 5 | 0.253 | 1.8743 | 0.8118 |
| balanced | 100 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.582 | 1.8743 | 0.9869 |
| aggressive | 200 | 400 | 0.1342 | 0.0469 | 2.8611 | 2 | 1.980 | 1.8743 | 0.9869 |

`balanced` 与 `aggressive` 得到相同的 Sharpe Ratio，均高于 `conservative`。`aggressive` 的运行时间更长，但没有带来额外提升，说明在当前数据上继续提高粒子数和迭代次数存在边际收益递减。

### 7.2 粒子数量对比

| particles | iterations | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | convergence_improvement |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 200 | 0.1452 | 0.0536 | 2.7083 | 2 | 0.313 | 0.8238 |
| 100 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.510 | 0.9069 |
| 200 | 200 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.918 | 0.9298 |

粒子数从 50 增加到 100 后，Sharpe Ratio 从 2.7083 提升到 2.8611；继续增加到 200 后最终 Sharpe Ratio 不再提升，但运行时间继续增加。因此粒子数增加可以提升搜索覆盖，但并非越大越好。

### 7.3 迭代次数对比

| iterations | particles | expected_return | volatility | sharpe_ratio | selected_assets_count | compute_time_seconds | convergence_improvement |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.299 | 0.9069 |
| 200 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.512 | 0.9069 |
| 400 | 100 | 0.1342 | 0.0469 | 2.8611 | 2 | 0.925 | 0.9069 |

在固定随机种子和参数下，100 次迭代已经达到后续 200 次和 400 次迭代相同的 Sharpe Ratio。收敛曲线在较早阶段趋于平台，继续增加迭代次数主要增加运行时间。

### 7.4 随机种子稳定性

| random_seed | expected_return | volatility | sharpe_ratio | selected_assets_count | monte_carlo_best_sharpe | pso_minus_monte_carlo_best_sharpe |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.1342 | 0.0469 | 2.8611 | 2 | 1.8803 | 0.9808 |
| 7 | 0.1342 | 0.0469 | 2.8611 | 2 | 1.8736 | 0.9875 |
| 42 | 0.1342 | 0.0469 | 2.8611 | 2 | 1.8743 | 0.9869 |
| 2024 | 0.1371 | 0.0484 | 2.8347 | 2 | 1.8812 | 0.9535 |
| 3407 | 0.1452 | 0.0536 | 2.7083 | 2 | 1.8775 | 0.8308 |

随机种子稳定性统计如下：

- `sharpe_ratio_mean = 2.8253`
- `sharpe_ratio_std = 0.0594`
- `expected_return_mean = 0.1370`
- `volatility_mean = 0.0485`
- `selected_assets_count_mean = 2.0`

大多数随机种子得到接近结果，但 seed 3407 的 Sharpe Ratio 较低，说明 PSO 仍受初始化和随机搜索过程影响。总体看，当前参数设置下结果较稳定，但不能据此声称算法保证全局最优。

## 8. Web 可视化界面

系统提供 Vue + ECharts Web 可视化界面，可通过以下命令启动本地系统：

```bash
make demo
```

启动后浏览器访问：

```text
http://127.0.0.1:5173
```

Web 界面支持 `conservative`、`balanced`、`aggressive` 三组预设参数，也支持手动调整粒子数、迭代次数、惯性权重、学习因子、无风险收益率、随机种子和 Monte Carlo 样本数。

界面展示内容包括：

- KPI：`expected_return`、`volatility`、`sharpe_ratio`、`selected_assets_count`、`cache_hit`、`compute_time_seconds`。
- PSO 收敛曲线：展示每轮迭代的全局最优 Sharpe Ratio。
- Top 10 权重图：展示最优组合中权重最高的候选策略。
- 风险-收益散点图：展示 Monte Carlo 随机组合与 PSO 最优解。
- 入选策略表：展示权重不低于 1% 的候选策略。
- Preset 对比图与组合权重对比图：展示不同 PSO 参数设置下 `expected_return`、`volatility`、`sharpe_ratio` 和最优组合结构的变化。

`cache_hit` 只表示系统命中了本地缓存。缓存结果来自此前相同参数下的真实计算，不改变算法定义，也不代表跳过项目中的 PSO 设计。

## 9. 项目总结与不足

本项目完成了从数据加载、数学建模、手写 PSO 优化、FastAPI 接口、Vue + ECharts 可视化到实验分析的完整闭环。实验结果表明，PSO 能在当前 UCI 候选策略权重空间和参数设置下找到 Sharpe Ratio 较高的组合，并且相对于 Monte Carlo 随机组合 baseline 具有更有方向的搜索过程。

项目局限包括：

- UCI 数据不是原始股票价格时间序列，当前建模是对候选策略的权重优化。
- 协方差矩阵只基于有限 period observations，存在低秩和估计不稳定问题。
- PSO 是启发式算法，不保证数学意义上的全局最优。
- 系统未接入实时市场数据。
- 系统未考虑交易成本、调仓频率、行业约束、流动性约束等真实投资限制。

后续可扩展方向包括：

- 引入真实股票价格序列，构造更稳定的收益率矩阵。
- 加入多目标优化，同时考虑收益、波动率、回撤等指标。
- 加入交易成本、调仓频率和仓位上限等约束。
- 增加更多优化算法对比，例如遗传算法、模拟退火或凸优化方法。
