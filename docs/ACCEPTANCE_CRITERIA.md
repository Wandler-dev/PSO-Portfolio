# 项目验收标准

## 1. 总体验收原则

项目最终应能完整说明并展示：

- 投资组合优化问题的决策变量。
- 最大化 Sharpe Ratio 的目标函数。
- `wi >= 0` 且 `sum(wi) = 1` 的约束条件。
- 手写 PSO 如何求解连续投资权重。
- 如何通过 1% 权重阈值解释股票选择结果。
- 数据源优先使用 UCI Stock Portfolio Performance 数据集，必要时降级使用本地样例数据或模拟数据。
- 日度价格数据按 252 个交易日年化。
- 最优组合的收益、`volatility`、Sharpe Ratio 和权重分布。
- Monte Carlo 风险-收益散点图、PSO 收敛曲线等可视化结果。

## 2. 环境与项目结构验收

验收标准：

- 项目位于 `/home/lenovo/projects/portfolio-pso`。
- conda 环境为 `portfolio-pso`。
- Python、pip、NumPy、Pandas、FastAPI 可用。
- Node.js 和 npm 可用。
- 存在基础目录：`backend/`、`frontend/`、`docs/`、`data/`、`notebooks/`、`scripts/`。
- 存在 `.gitignore`。
- `backend/health_check.py` 能打印 Python 和关键依赖版本。

验收命令：

```bash
printenv CONDA_DEFAULT_ENV
python backend/health_check.py
node --version
npm --version
```

通过条件：

- `CONDA_DEFAULT_ENV` 输出 `portfolio-pso`。
- `health_check.py` 正常输出 Python、NumPy、Pandas、FastAPI 版本。
- Node.js 和 npm 输出版本号。

## 2.1 文档冻结验收

验收标准：

- 四份核心文档和新增文档之间，目标函数、约束条件、字段命名必须一致。
- 不得出现 Sharpe Ratio 错误公式。
- 不得将 1% 阈值写成优化约束。
- 不得将 15% 单票仓位上限写成 V1 必做约束。

通过条件：

- Sharpe Ratio 统一写为 `(E(Rp) - Rf) / volatility`。
- `volatility` 统一写为 `sqrt(w^T Sigma w)` 或等价矩阵形式。
- 对外字段统一使用 `expected_return`、`volatility`、`sharpe_ratio`、`best_weights`、`selected_assets`。

## 3. 数学建模验收

验收标准：

- 文档和代码均将粒子定义为连续权重向量 `w = [w1, w2, ..., wN]`。
- 权重满足 `wi >= 0`。
- 权重满足 `sum(wi) = 1`。
- 目标函数为最大化 Sharpe Ratio。
- 组合波动率计算使用 `volatility = sqrt(w^T Sigma w)`。
- 组合收益计算使用 `E(Rp) = w^T mu`。
- 若输入为日度价格数据，默认使用 252 个交易日年化：`mu_annual = mean_daily_return * 252`，`Sigma_annual = cov_daily_return * 252`。
- 外部 API 和前端字段使用 `volatility` 表示组合风险/波动率；报告中可解释为“风险，即组合波动率”。
- 1% 阈值只用于解释股票是否被选择。

通过条件：

- 任意优化输出的权重和与 1 的误差不超过 `1e-6`。
- 任意输出权重不小于 `-1e-12`，数值误差范围内可视为 0。
- 文档、接口字段和前端展示对目标函数、年化口径和 `volatility` 字段命名的表述一致。

## 4. PSO 算法验收

验收标准：

- PSO 核心算法为项目内手写实现。
- 未使用 `scipy.optimize`。
- 未使用 `pyswarms`。
- 未使用其他黑盒优化库直接求解投资组合问题。
- 粒子位置更新后执行非负处理和归一化。
- 固定随机种子时，优化结果可复现。
- 每轮迭代记录全局最优 Sharpe Ratio。
- 输出最优权重、最优收益率、最优 `volatility`、最优 Sharpe Ratio。

通过条件：

- 使用固定随机种子连续运行两次，关键输出一致。
- 收敛曲线数据长度与迭代次数一致。
- `convergence_curve` 长度必须等于 `iterations`。
- `best_weights` 长度必须等于资产数量 `N`。
- `min(best_weights) >= -1e-12`。
- `abs(sum(best_weights)-1) <= 1e-6`。
- 固定 `random_seed` 后，两次运行输出的 `best_weights`、`sharpe_ratio` 应保持一致或在数值容差内一致。
- 最优权重满足约束。
- 对 `volatility` 接近 0 的情况有明确保护逻辑，不出现未处理的除零错误。

禁止通过条件：

- 只调用第三方优化函数而没有手写 PSO 更新过程。
- 用离散选股算法替代连续权重优化。
- 将 1% 阈值直接写入 PSO 位置更新约束。

## 5. 数据接入验收

验收标准：

- 数据至少包含日期、股票标识、价格字段。
- 数据源优先级为 UCI Stock Portfolio Performance 数据集，其次为本地样例数据或模拟数据。
- 数据清洗规则明确。
- 能从价格数据计算收益率矩阵。
- 能从日度收益率矩阵计算年化期望收益向量和年化协方差矩阵。
- 缺失值、非数值、价格异常时有处理规则或错误提示。
- 若 UCI 数据因网络或字段问题不可用，报告中必须说明降级原因和替代数据来源。

通过条件：

- 同一份输入数据可重复生成一致的收益率矩阵。
- 收益率矩阵维度与股票池数量一致。
- 协方差矩阵为方阵，维度为 `N x N`。
- 日度输入的年化计算使用 252 个交易日。
- 当有效股票数量不足时，系统返回明确错误，不继续输出伪结果。

## 6. FastAPI 接口验收

验收标准：

- 提供健康检查接口。
- 提供优化运行接口。
- 请求参数包含股票池或数据选择、PSO 参数、无风险收益率。
- 响应包含最优权重、被选择股票、收益率、`volatility`、Sharpe Ratio。
- 响应包含前端图表所需数据。
- 响应中组合风险/波动率字段统一命名为 `volatility`。
- 非法参数返回明确错误信息。

优化接口响应至少包含：

```text
best_weights
selected_assets
expected_return
volatility
sharpe_ratio
convergence_curve
risk_return_points
best_point
```

其中 `risk_return_points` 默认来自不少于 2000 个 Monte Carlo 随机组合，PSO 最优组合应通过单独字段或标记供前端高亮展示。

通过条件：

- 正常请求返回成功响应。
- 非法参数不会导致服务崩溃。
- 返回字段能支撑前端全部图表。
- `risk_return_points` 数量不少于 2000，除非请求参数显式指定更小数量用于调试。
- `risk_return_points` 默认不少于 2000 个随机组合。
- 每个点至少包含 `volatility`、`expected_return`、`sharpe_ratio`。
- `best_point` 必须包含 `volatility`、`expected_return`、`sharpe_ratio`。

## 7. 前端看板验收

验收标准：

- 使用 Vue 3。
- 使用 Element Plus 构建基础交互控件。
- 使用 ECharts 绘制图表。
- 页面提供 PSO 参数输入。
- 页面能触发后端优化接口。
- 页面展示最优组合摘要。
- 页面展示权重分布。
- 页面展示被选择股票列表。
- 页面展示 Monte Carlo 风险-收益散点图。
- 页面展示 PSO 收敛曲线。
- 页面具有加载状态、错误状态和空数据状态。

通过条件：

- 启动前端后可完成一次完整优化流程。
- 图表非空，且数据来自后端响应。
- 权重大于等于 1% 的股票在“已选择”结果中展示。
- 风险-收益散点图默认包含不少于 2000 个随机组合。
- PSO 最优组合在风险-收益散点图中有明显高亮标记。
- 前端必须高亮 `best_point`。

## 8. 实验报告与答辩验收

验收标准：

- 报告说明课程背景和问题定义。
- 报告明确决策变量、目标函数和约束条件。
- 报告说明 PSO 粒子表示、初始化、速度更新、位置更新和约束处理。
- 报告说明 UCI Stock Portfolio Performance 数据集优先级、实际数据来源和数据处理方式。
- 若使用本地样例数据或模拟数据降级，报告说明 UCI 数据不可用原因。
- 报告说明日度价格数据按 252 个交易日年化的收益率和风险计算口径。
- 报告展示最优投资组合权重。
- 报告展示 Monte Carlo 风险-收益散点图，默认不少于 2000 个随机组合。
- 报告展示 PSO 收敛曲线。
- 报告解释 1% 权重阈值的含义。
- 报告将 `volatility` 解释为组合风险/波动率。
- 报告总结实验结果和局限性。

通过条件：

- 答辩材料能独立解释系统做了什么、如何建模、如何求解、结果如何。
- 图表和系统输出一致，PSO 最优组合在风险-收益散点图中高亮。
- 报告没有把黑盒优化库描述为项目核心算法。

## 9. 文档验收

验收标准：

- 存在 `docs/PROJECT_PLAN.md`。
- 存在 `docs/PROPOSAL_REVISED.md`。
- 存在 `docs/CODEX_INSTRUCTIONS.md`。
- 存在 `docs/ACCEPTANCE_CRITERIA.md`。
- 四份文档对项目名称、数据源优先级、252 交易日年化口径、`volatility` 字段命名、Monte Carlo baseline、目标函数、约束条件、技术栈和 PSO 限制的表述一致。

通过条件：

- 后续开发者只阅读这四份文档，即可理解项目范围、阶段计划、核心算法约束和验收标准。

## 10. 一票否决项

出现以下任一情况，项目不得视为通过：

- 无法说明决策变量、目标函数或约束条件。
- PSO 核心算法使用黑盒优化库替代。
- 输出权重不满足非负和归一化约束。
- 没有风险-收益散点图。
- 风险-收益散点图没有 Monte Carlo 随机组合 baseline 或没有高亮 PSO 最优组合。
- 没有展示最优组合权重。
- 没有解释 1% 权重阈值。
- 没有说明数据源优先级、数据降级原因或 252 交易日年化口径。
- 后端接口无法完成一次优化流程。
- 前端无法展示后端优化结果。
- 报告与系统实现的目标函数或约束条件不一致。
