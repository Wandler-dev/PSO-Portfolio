# 答辩讲解要点

## 1. 30 秒项目简介

本项目是一个基于粒子群优化算法的投资组合风险-收益均衡决策系统。系统把投资组合表示为连续权重向量，在非负且权重和为 1 的约束下，使用手写 PSO 最大化 Sharpe Ratio。后端完成数据加载、优化计算和 API 封装，前端用 Vue 3 与 ECharts 展示参数调整、收敛曲线、权重分布、风险-收益散点图和入选策略。

## 2. 1 分钟算法建模说明

- 决策变量是 `w=[w1,w2,...,wN]`，每个 `wi` 表示一个候选策略的资金占比。
- 约束是 `wi >= 0` 且 `sum(wi)=1`，表示不卖空且资金全部分配。
- 目标函数是最大化 `Sharpe Ratio=(E(Rp)-Rf)/volatility`。
- `E(Rp)=w^T mu`，`volatility=sqrt(w^T Sigma w)`。
- PSO 中每个粒子是一组权重，每轮更新速度和位置后，都进行非负处理与归一化。
- 1% 权重阈值只用于解释哪些策略被实质选中，不参与优化约束。

## 3. 1 分钟系统实现说明

- 数据层读取 UCI Excel，将每个 ID 解释为一个候选 stock-selection weighting strategy。
- 后端使用 NumPy、Pandas、FastAPI；PSO 核心算法手写。
- `expected_returns` 来自 `all period` 的 `original_Annual Return`。
- `covariance_matrix` 由 1st/2nd/3rd/4th period 的 Annual Return observations 构造。
- API 返回统一字段：`expected_return`、`volatility`、`sharpe_ratio`、`best_weights`、`selected_assets` 等。
- 前端通过 `/api/optimize` 获取结果，并用 ECharts 展示收敛曲线、权重图和风险-收益散点图。

## 4. 1 分钟 Demo 演示路线

1. 打开看板，先说明顶部数据源、候选策略数量和后端连接状态。
2. 在左侧选择 `balanced` preset，展示 PSO 参数。
3. 点击“开始优化”，观察 KPI 指标变化。
4. 查看收敛曲线，说明 PSO 全局最优 Sharpe Ratio 随迭代提升并趋于稳定。
5. 查看风险-收益散点图，比较 Monte Carlo 随机组合与 PSO 最优解。
6. 查看权重 Top 10 和入选策略表，解释 1% 阈值的展示含义。

## 5. 常见问题与回答

### 你们优化的变量是什么？

优化变量是连续权重向量 `w=[w1,w2,...,wN]`，每个权重表示资金分配比例。PSO 搜索的是权重组合，不是离散选股标签。

### UCI 数据不是股票价格，为什么还能做投资组合优化？

该 UCI 数据描述的是 weighted scoring stock portfolios 的表现。我们将每个 ID 解释为一个候选 stock-selection weighting strategy，优化的是这些候选策略之间的资金分配权重，而不是直接优化单只股票价格序列。

### 63 个候选策略是什么意思？

数据加载后有效 ID 数量为 63。每个 ID 对应一种基于不同选股概念权重形成的候选策略，本项目用 `Strategy_ID` 表示它们。

### PSO 是否保证全局最优？

不保证。PSO 是启发式优化算法，可以在连续空间中进行有方向的搜索，但不能证明一定找到数学意义上的全局最优。因此报告中表述为近似最优或当前实验中的较优组合。

### 为什么要用 Monte Carlo baseline？

Monte Carlo baseline 随机生成大量合法权重组合，用于提供直观对比。它不是理论最优解，但能说明 PSO 解相对随机搜索结果是否更好。

### 为什么不需要大规模训练？

本项目不是监督学习模型，没有训练神经网络或回归模型。PSO 是直接在权重空间中优化目标函数，因此主要计算过程是迭代搜索，不是大规模训练。

### 1% 阈值的作用是什么？

1% 阈值只用于结果解释。权重 `>= 1%` 的策略显示为入选策略，方便答辩讲解；该阈值不参与 PSO 的位置更新、约束处理或目标函数计算。

### 协方差矩阵怎么来的？

使用 1st/2nd/3rd/4th period 的 Annual Return observations 按 ID 对齐，形成 period-level returns matrix，再用 `np.cov(..., rowvar=False)` 计算协方差矩阵。

### 为什么不用 252 日年化？

252 日年化适用于日度价格或日收益率数据。UCI 的 Annual Return 已经是 performance-level 指标，不是日收益率，因此不能再乘以 252，否则会重复年化。

### 缓存/预计算是否影响算法真实性？

不影响。缓存只保存相同参数下已经计算过的完整响应，用于答辩 Demo 加速。用户自定义参数仍按相同 PSO 算法实时计算，缓存不改变目标函数、约束或优化结果。
