# 最终课程报告大纲

## 1. 项目背景

- 说明投资组合优化问题：在有限资金下分配资产权重，追求收益和风险的平衡。
- 说明课程任务要求：明确决策变量、目标函数、约束条件，并展示优化结果。
- 说明本系统定位：课程展示系统，不是实盘交易系统，也不提供投资建议。
- 说明选用 PSO 的原因：适合连续权重搜索，能直观展示迭代收敛过程。

## 2. 数据集说明

- 数据源优先使用 UCI Stock Portfolio Performance 数据集。
- 说明该数据集不是 `date/symbol/close` 原始股票价格表。
- 解释每个 UCI ID 被建模为一个候选 stock-selection weighting strategy。
- 说明 `expected_returns` 和 `covariance_matrix` 的构造方式。
- 说明不对 UCI Annual Return 重复进行 252 日年化。

## 3. 投资组合优化建模

- 决策变量为连续权重向量 `w=[w1,w2,...,wN]`。
- 约束条件为 `wi >= 0` 且 `sum(wi)=1`。
- 目标函数为最大化 `Sharpe Ratio=(E(Rp)-Rf)/volatility`。
- 组合收益为 `E(Rp)=w^T mu`。
- 组合波动率为 `volatility=sqrt(w^T Sigma w)`。

## 4. PSO 算法设计

- 说明粒子表示：每个粒子是一组候选策略权重。
- 说明初始化：随机生成粒子位置，并进行非负归一化。
- 说明速度更新、位置更新、个体最优和全局最优。
- 说明每轮更新后执行权重非负处理和归一化。
- 说明 1% 阈值只用于解释入选策略，不参与搜索约束。

## 5. 系统实现

- 后端使用 Python、NumPy、Pandas、FastAPI。
- PSO 核心算法手写，不使用 `scipy.optimize`、`pyswarms` 或黑盒优化库。
- 数据加载器将 UCI Excel 转换为 `expected_returns` 和 `covariance_matrix`。
- API 提供健康检查、数据摘要、presets 和优化接口。
- 前端使用 Vue 3、Element Plus、ECharts 展示 Demo 看板。

## 6. 实验设计

- 使用 UCI 数据运行可复现实验。
- 实验固定 `risk_free_rate=0.0`，Monte Carlo baseline 样本数为 3000。
- 设计 preset 对比、粒子数量对比、迭代次数对比、随机种子稳定性四组实验。
- 记录 Sharpe Ratio、expected_return、volatility、selected_assets_count 和运行时间。
- 使用 Monte Carlo 随机组合 baseline 比较 PSO 解的相对表现。

## 7. 实验结果

- 展示 preset 对比表格，说明 balanced 与 aggressive 在本次实验中表现接近。
- 展示粒子数量影响，说明粒子数增加后存在边际收益递减。
- 展示迭代次数影响，说明部分参数下收敛曲线趋于平台。
- 展示随机种子稳定性，说明 PSO 结果总体稳定但仍有随机波动。
- 强调 PSO 高于 Monte Carlo baseline，但不保证全局最优。

## 8. Web Demo 展示

- 展示左侧参数面板：presets 和自定义 PSO 参数。
- 展示 KPI：expected_return、volatility、sharpe_ratio、selected_assets_count。
- 展示 PSO 收敛曲线。
- 展示最优组合权重 Top 10。
- 展示风险-收益散点图，并高亮 PSO 最优解。

## 9. 总结与不足

- 总结系统完成了从数据加载、PSO 优化、API 封装到前端展示的闭环。
- 总结 PSO 可以在候选策略权重空间中搜索较高 Sharpe Ratio 的组合。
- 说明 UCI 数据不是原始股票价格，因此建模解释存在边界。
- 说明协方差矩阵基于有限 period observations，估计稳定性有限。
- 后续可扩展真实价格数据、更复杂风险偏好参数和 V2 可选图表。
