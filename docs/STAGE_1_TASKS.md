# 阶段一任务单：后端算法原型

## 1. 阶段目标

只实现后端算法原型，跑通 PSO 投资组合优化闭环。不做 FastAPI，不做 Vue 前端，不接真实 UCI 数据。

## 2. 必须创建的文件

- `backend/app/portfolio_math.py`
- `backend/app/pso_optimizer.py`
- `backend/app/random_baseline.py`
- `backend/run_demo.py`
- `tests/test_portfolio_math.py`
- `tests/test_pso_optimizer.py`

## 3. portfolio_math.py 功能

必须实现：

- `normalize_weights(weights)`
- `portfolio_expected_return(weights, expected_returns)`
- `portfolio_volatility(weights, covariance_matrix)`
- `sharpe_ratio(weights, expected_returns, covariance_matrix, risk_free_rate=0.0)`

要求：

- `normalize_weights` 必须保证非负和归一化。
- `portfolio_volatility` 必须使用 `sqrt(w^T Sigma w)`。
- `sharpe_ratio` 必须处理 `volatility` 接近 0 的情况。

## 4. pso_optimizer.py 功能

必须实现：

- 手写 `PSOOptimizer` 类或 `run_pso` 函数。
- 输入 `expected_returns`、`covariance_matrix`、`particles`、`iterations`、`inertia_weight`、`c1`、`c2`、`risk_free_rate`、`random_seed`。
- 输出 `best_weights`、`expected_return`、`volatility`、`sharpe_ratio`、`convergence_curve`。
- 每次位置更新后执行 `normalize_weights`。
- 固定 `random_seed` 后结果可复现。

## 5. random_baseline.py 功能

必须实现：

- `generate_random_portfolios(...)`
- 默认生成不少于 2000 个随机组合。
- 每个随机组合输出 `volatility`、`expected_return`、`sharpe_ratio`。
- 用于后续风险-收益散点图。

## 6. run_demo.py 功能

必须实现：

- 构造固定 `random_seed` 的模拟 `expected_returns` 和 `covariance_matrix`。
- 运行 PSO。
- 运行 Monte Carlo baseline。
- 打印最优权重、`expected_return`、`volatility`、`sharpe_ratio`。
- 打印 `selected_assets`，即权重 `>= 1%` 的资产。
- 不依赖前端和 FastAPI。

## 7. 测试要求

`pytest` 至少覆盖：

- 权重归一化后 `sum=1`。
- 权重非负。
- `volatility` 计算公式正确。
- Sharpe Ratio 公式正确。
- `convergence_curve` 长度等于 `iterations`。
- 固定 `random_seed` 结果可复现。
- 未引入 `scipy.optimize` 和 `pyswarms`。

## 8. 验收命令

必须能通过：

```bash
pytest
python backend/run_demo.py
```

## 9. 禁止事项

- 不做 FastAPI。
- 不做前端。
- 不接真实数据。
- 不使用 `scipy.optimize`。
- 不使用 `pyswarms`。
- 不把 1% 阈值写入 PSO 优化约束。
