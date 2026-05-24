# 数据规范

## 1. 数据源优先级

1. 优先使用 UCI Stock Portfolio Performance 数据集。
2. 若 UCI 失败，使用 `data/sample/` 本地样例数据。
3. 若阶段一尚未接入真实数据，允许使用模拟数据。
4. 输出中必须记录 `data_source`。

`data_source` 推荐取值：

- `uci`：课程要求提供的 UCI Stock Portfolio Performance 数据集。
- `sample`：`data/sample/` 下的本地样例数据。
- `simulated`：阶段一算法原型使用的固定随机种子模拟数据。

## 2. 标准内部数据结构

- `asset_names: list[str]`
- `returns_matrix`：二维矩阵，形状为 `T x N`
- `expected_returns`：长度为 `N`
- `covariance_matrix`：`N x N`
- `annualized: bool`
- `trading_days_per_year`：默认 252

结构说明：

- `T` 表示有效时间样本数量。
- `N` 表示有效资产数量。
- `expected_returns` 和 `covariance_matrix` 必须使用同一组资产顺序。
- 若 `annualized` 为 `true`，后续流程不得重复年化。

## 3. 价格数据处理流程

1. 按资产和日期排序。
2. 计算收益率。
3. 处理缺失值。
4. 删除有效样本不足的资产。
5. 计算 `expected_returns` 和 `covariance_matrix`。
6. 进行年化处理。

处理流程必须保证进入 PSO 的收益向量和协方差矩阵维度一致。

## 4. 年化规则

- `expected_returns = mean_daily_returns * 252`
- `covariance_matrix = daily_covariance_matrix * 252`
- `volatility = sqrt(w^T covariance_matrix w)`

若输入数据已经是年化指标，则不得重复年化，必须将 `annualized` 标记为 `true`，并在数据说明中写明来源。

## 5. 数据质量检查

- 有效资产数量必须 `>= 2`。
- `covariance_matrix` 必须是 `N x N` 方阵。
- `expected_returns` 长度必须等于 `N`。
- 不允许 `NaN` 或 `inf` 进入 PSO。
- 如果数据无效，必须返回明确错误。

数据质量错误不得通过填充伪结果掩盖。若降级到本地样例数据或模拟数据，必须在输出中记录 `data_source`。

## 6. 阶段一模拟数据规则

- 模拟数据只用于算法原型。
- 模拟数据需要固定 `random_seed`。
- 模拟数据资产数量建议 8 到 20。
- 模拟数据结果不得在最终报告中冒充真实数据实验。

阶段一模拟数据的目标是验证权重归一化、Sharpe Ratio、PSO 收敛曲线和 Monte Carlo baseline 等算法闭环，不承担真实金融数据结论。
