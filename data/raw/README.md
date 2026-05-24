# UCI Stock Portfolio Performance 数据说明

本目录用于存放课程项目所需的原始数据文件。当前项目优先使用 UCI Machine Learning Repository 提供的 Stock Portfolio Performance 数据集。

## 1. 数据来源

- 数据集名称：Stock Portfolio Performance
- 来源：UCI Machine Learning Repository
- 官方链接：https://archive.ics.uci.edu/ml/datasets/Stock+portfolio+performance
- 本地原始文件名：`stock portfolio performance data set.xlsx`

项目中建议识别以下两个文件名：

- `data/raw/uci_stock_portfolio_performance.xlsx`
- `data/raw/stock portfolio performance data set.xlsx`

其中，`uci_stock_portfolio_performance.xlsx` 是项目内部推荐的规范文件名；如果该文件不存在，程序可以回退读取 UCI 原始下载文件名 `stock portfolio performance data set.xlsx`。

## 2. 数据集基本信息

根据 UCI 官方说明，该数据集并不是传统的股票价格时间序列数据，也不是 `date / symbol / close` 格式的数据表。

该数据集描述的是 weighted scoring stock portfolios 的表现数据。也就是说，数据集中每一条记录对应一种基于选股概念权重组合形成的投资组合方案。研究者通过 mixture design 生成不同的选股概念权重组合，再利用美国股票市场历史数据库模拟这些组合的投资表现。

UCI 官方信息包括：

| 项目 | 内容 |
|---|---|
| Dataset ID | 390 |
| 数据类型 | Multivariate |
| 任务类型 | Regression |
| 实例数 | 315 |
| 特征数 | 12 |
| 缺失值 | No |
| 文件格式 | `.xlsx` |

## 3. 官方变量含义

该数据集主要包含 6 个输入变量和 6 个输出变量。

### 3.1 输入变量：选股概念权重

这些变量表示不同 stock-picking concepts 在 weighted scoring stock selection model 中的权重。

| 变量 | 含义 |
|---|---|
| X1 | Large B/P |
| X2 | Large ROE |
| X3 | Large S/P |
| X4 | Large Return Rate in the last quarter |
| X5 | Large Market Value |
| X6 | Small systematic Risk |

这些变量不是股票价格，也不是股票本身，而是构造投资组合时使用的选股概念权重。

### 3.2 输出变量：投资表现指标

这些变量表示对应权重组合在历史市场模拟中的表现。

| 变量 | 含义 |
|---|---|
| Y1 | Annual Return |
| Y2 | Excess Return |
| Y3 | Systematic Risk |
| Y4 | Total Risk |
| Y5 | Abs. Win Rate |
| Y6 | Rel. Win Rate |

本项目最关注以下字段：

- `Annual Return`
- `Total Risk`
- `Systematic Risk`

它们可用于构造投资组合优化中的收益与风险输入。

## 4. 本地数据画像结果

当前本地 Excel 文件为：

- `data/raw/stock portfolio performance data set.xlsx`

通过 `scripts/profile_uci_dataset.py` 画像后发现，该 Excel 文件包含 6 个 sheet：

- `4th period`
- `3rd period`
- `2nd period`
- `1st period`
- `all period`
- `Time frame`

各 sheet 结构如下：

| Sheet | 形状 |
|---|---|
| 4th period | 64 rows × 19 columns |
| 3rd period | 64 rows × 19 columns |
| 2nd period | 64 rows × 19 columns |
| 1st period | 64 rows × 19 columns |
| all period | 64 rows × 19 columns |
| Time frame | 5 rows × 4 columns |

画像结论：

- 前 5 个 period sheet 均为 64 × 19。
- `Time frame` sheet 为 5 × 4。
- 未发现带 `%` 的字符串。
- 每个 sheet 都存在非数值字段。
- Excel 表头结构较复杂，默认读取时部分列名会被解析为 `Unnamed:*`。
- 实际指标名可能出现在数据首行，因此不能直接使用 Pandas 默认表头作为最终字段名。
- 该数据集不适合直接整体当作价格序列计算日收益率和协方差矩阵。

## 5. 对本项目的解释方式

由于该 UCI 数据集不是原始股票价格数据，因此本项目不能按如下方式处理：

    股票价格数据 -> 日收益率 -> 年化收益率 -> 协方差矩阵

本项目更适合采用如下解释：

    UCI 每个 ID 对应一种 stock-selection weighting combination
    每个 ID 可视为一个候选投资策略 Strategy_ID
    不同 period 的 Annual Return 可视为该候选策略在不同阶段的收益表现

因此，阶段二数据加载器中建议采用：

    asset_names = Strategy_1, Strategy_2, ..., Strategy_N

这里的 `asset_names` 并不表示真实股票代码，而表示候选投资策略或候选组合方案。

## 6. 推荐数据解析策略

### 6.1 表头重建

由于画像显示默认列名中存在 `Unnamed:*`，数据加载器不应直接使用 Pandas 默认表头。

建议做法：

1. 读取每个 period sheet。
2. 检查前几行内容。
3. 找到真实字段名所在行。
4. 重建列名。
5. 删除无效表头行和空行。
6. 将收益、风险等字段转换为数值类型。

### 6.2 expected_returns 构造策略

优先方案：

    expected_returns = all period sheet 中的 Annual Return

备选方案：

    expected_returns = 1st / 2nd / 3rd / 4th period 中 Annual Return 的均值

选择字段时应优先匹配：

- `Annual Return`

如果字段名存在变体，可以使用大小写不敏感和模糊匹配，例如：

- `annual`
- `return`
- `annual return`

### 6.3 covariance_matrix 构造策略

优先方案：

使用 `1st period`、`2nd period`、`3rd period`、`4th period` 的 `Annual Return` 构造收益观察矩阵：

    returns_matrix shape = 4 × N

其中：

- 行表示不同 period。
- 列表示不同 Strategy_ID。

然后计算：

    covariance_matrix = np.cov(returns_matrix, rowvar=False)

此时需要在 `source_notes` 中说明：

    covariance_matrix is estimated from period-level Annual Return observations.

备选方案：

如果无法稳定从多个 period 中对齐 `Annual Return`，则使用 `Total Risk` 构造对角协方差矩阵：

    covariance_matrix = np.diag(total_risk ** 2)

此时需要在 `source_notes` 中明确说明：

    diagonal covariance fallback is used; cross-strategy correlations are not estimated.

兜底方案：

如果 UCI 文件不存在、字段无法解析或数据质量检查失败，则使用模拟数据：

    data_source = simulated_fallback

不得将模拟数据伪装成 UCI 真实数据。

## 7. 年化规则说明

本项目的通用数据规范中规定：如果输入为日度价格数据，则默认使用 252 个交易日进行年化：

    expected_returns = mean_daily_returns * 252
    covariance_matrix = daily_covariance_matrix * 252

但 UCI Stock Portfolio Performance 数据集不是日度价格数据，而是 period-level / performance-level 指标数据。

因此，对于该 UCI 数据集：

    不要套用 252 日年化规则。

如果使用 `Annual Return` 字段，则应将其视为数据集中已经给定的表现指标，不再重复乘以 252。

## 8. 数据加载器输出要求

后续 `backend/app/data_loader.py` 应将该数据集转换为阶段一 PSO 可直接使用的标准格式：

    {
      "data_source": "uci",
      "asset_names": [...],
      "expected_returns": np.ndarray,
      "covariance_matrix": np.ndarray,
      "annualized": True,
      "trading_days_per_year": None,
      "source_notes": "..."
    }

字段说明：

| 字段 | 含义 |
|---|---|
| data_source | 数据来源，例如 `uci` 或 `simulated_fallback` |
| asset_names | 候选策略名称，例如 `Strategy_1` |
| expected_returns | 每个候选策略的期望收益 |
| covariance_matrix | 候选策略之间的协方差矩阵 |
| annualized | 是否已是年化或 period-level 表现指标 |
| trading_days_per_year | 若不是日度价格数据，可设为 `None` |
| source_notes | 记录具体解析方式、字段来源和兜底情况 |

## 9. 数据质量检查要求

进入 PSO 之前必须检查：

- `asset_names` 数量 >= 2
- `expected_returns` 是长度为 N 的一维数组
- `covariance_matrix` 是 N × N 方阵
- `expected_returns` 不包含 NaN 或 inf
- `covariance_matrix` 不包含 NaN 或 inf
- `covariance_matrix` 维度与 `asset_names` 数量一致
- `covariance_matrix` 对角线不能为负

如果检查失败，程序必须返回明确错误，不能继续输出伪结果。

## 10. 与课程项目的关系

课程任务要求是投资组合优化：在有限资金下选择投资组合，使收益最大化并控制风险。

由于 UCI 数据集本身并不是股票价格表，本项目在使用该数据集时采取如下建模解释：

    每个 UCI ID 对应一个候选投资策略或候选组合方案；
    PSO 优化的是这些候选策略之间的资金分配权重；
    目标是最大化 Sharpe Ratio；
    约束是 wi >= 0 且 sum(wi) = 1；
    1% 阈值只用于解释某个候选策略是否被实质选入组合。

这与阶段一中抽象的投资组合优化接口保持一致：

    expected_returns + covariance_matrix -> PSO -> best_weights

## 11. 注意事项

1. 不要假设该数据集包含股票代码、日期和收盘价。
2. 不要使用 `date / symbol / close` 逻辑解析该数据集。
3. 不要对 UCI 的 `Annual Return` 重复做 252 日年化。
4. 不要把每一列解释为一只股票。
5. 不要把每一行简单解释为一只股票。
6. 更合适的解释是：每个 ID 是一个候选 stock-selection weighting combination。
7. 如果使用 `Total Risk` 构造对角协方差矩阵，需要在报告中说明没有估计策略间相关性。
8. 如果最终使用模拟数据兜底，报告中必须明确标注，不得冒充真实 UCI 实验结果。

## 12. Git 管理建议

`data/raw/` 下的原始 Excel 文件通常不建议提交到 Git。

建议 `.gitignore` 中包含：

- `data/raw/`
- `data/cache/`

代码、画像脚本和数据说明文档可以提交：

- `scripts/profile_uci_dataset.py`
- `docs/uci_dataset_profile.md`
- `data/raw/README.md`

原始数据文件可以在最终课程压缩包中单独包含，或由说明文档引导下载。

## 13. 当前项目推荐读取顺序

后续开发者在编写数据加载器前，应按顺序阅读：

1. `data/raw/README.md`
2. `docs/uci_dataset_profile.md`
3. `docs/DATA_SPEC.md`
4. `docs/API_CONTRACT.md`
5. `docs/STAGE_1_TASKS.md`

然后再实现：

- `backend/app/data_loader.py`
- `backend/run_data_demo.py`
- `tests/test_data_loader.py`