# API 数据契约

## 1. 字段命名原则

统一字段：

- `expected_return`
- `volatility`
- `sharpe_ratio`
- `best_weights`
- `selected_assets`
- `convergence_curve`
- `risk_return_points`
- `best_point`
- `asset_weight_table`
- `data_source`

禁止对外字段：

- `risk`
- `sigma_p`
- `best_sharpe`

这些禁止字段可作为内部局部变量短暂存在，但不得出现在 API 响应、前端类型定义或对外文档的数据契约中。

## 2. GET /api/health

用途：检查后端服务是否可用，以及数据源是否已准备好。

响应示例：

```json
{
  "status": "ok",
  "service": "portfolio-pso-backend",
  "data_source_ready": true
}
```

字段说明：

- `status`：服务状态，正常时为 `ok`。
- `service`：服务名称。
- `data_source_ready`：当前数据源是否可用于优化流程。

## 3. GET /api/data/summary

用途：返回当前数据源摘要，供前端展示数据状态。

响应示例：

```json
{
  "data_source": "uci",
  "asset_count": 63,
  "sample_count": 1000,
  "annualized": true,
  "trading_days_per_year": 252,
  "asset_names": ["Asset_1", "Asset_2"]
}
```

字段说明：

- `data_source`：数据来源，可为 `uci`、`sample`、`simulated`。
- `asset_count`：有效资产数量。
- `sample_count`：有效样本数量。
- `annualized`：是否已经年化。
- `trading_days_per_year`：年化使用的交易日数量，默认 252。
- `asset_names`：资产名称或资产编号列表。

## 4. POST /api/optimize

用途：运行 PSO 投资组合优化，并返回图表和表格所需数据。

请求示例：

```json
{
  "particles": 100,
  "iterations": 200,
  "inertia_weight": 0.7,
  "c1": 1.5,
  "c2": 1.5,
  "risk_free_rate": 0.0,
  "random_seed": 42,
  "monte_carlo_samples": 3000
}
```

响应示例：

```json
{
  "data_source": "uci",
  "asset_count": 63,
  "expected_return": 0.152,
  "volatility": 0.018,
  "sharpe_ratio": 8.44,
  "best_weights": [0.1, 0.2, 0.7],
  "selected_assets": [
    {
      "asset_id": "Asset_1",
      "weight": 0.1
    }
  ],
  "convergence_curve": [
    {
      "iteration": 1,
      "sharpe_ratio": 1.23
    }
  ],
  "risk_return_points": [
    {
      "volatility": 0.02,
      "expected_return": 0.12,
      "sharpe_ratio": 6.0,
      "type": "random"
    }
  ],
  "best_point": {
    "volatility": 0.018,
    "expected_return": 0.152,
    "sharpe_ratio": 8.44,
    "type": "pso_best"
  },
  "asset_weight_table": [
    {
      "asset_id": "Asset_1",
      "weight": 0.1,
      "selected": true
    }
  ]
}
```

响应要求：

- `best_weights` 长度必须等于 `asset_count`。
- `selected_assets` 只用于解释权重不低于 1% 的资产，不参与 PSO 搜索约束。
- `convergence_curve` 长度必须等于请求中的 `iterations`。
- `risk_return_points` 默认不少于 2000 个点。
- `best_point` 必须用于前端高亮 PSO 最优解。

## 5. 参数校验规则

- `particles` 范围：20 到 300。
- `iterations` 范围：50 到 500。
- `inertia_weight` 范围：0.1 到 1.5。
- `c1` 范围：0.5 到 3.0。
- `c2` 范围：0.5 到 3.0。
- `monte_carlo_samples` 默认 3000，最小 2000。

参数不满足范围时，后端必须返回明确错误响应，不得静默修正为其他值。

## 6. 错误响应格式

响应示例：

```json
{
  "error": true,
  "message": "iterations must be between 50 and 500",
  "field": "iterations"
}
```

字段说明：

- `error`：错误标记，错误响应中为 `true`。
- `message`：可读错误说明。
- `field`：触发错误的字段名；若为全局错误，可使用 `null`。
