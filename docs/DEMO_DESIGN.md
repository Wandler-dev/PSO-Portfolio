# Demo 设计文档

## 1. Demo 目标

本 Demo 不是实盘交易系统，不提供投资建议，也不包含交易、下单、账户或持仓同步能力。Demo 的定位是课程展示系统，用于说明如何将投资组合优化问题建模为连续权重优化问题，并展示手写 PSO 如何搜索投资组合、如何收敛，以及如何相对 Monte Carlo 随机组合取得更优的风险-收益权衡。

Demo 必须服务课程答辩：讲清楚决策变量、约束条件、目标函数、PSO 优化过程、随机 baseline 对比和最终持仓解释。

## 2. 演示主线

1. 调参数：调整 `particles`、`iterations`、`inertia_weight`、`c1`、`c2`。
2. 运行优化：点击按钮调用后端 API。
3. 看收敛：观察 `convergence_curve`。
4. 比基准：在风险-收益散点图中比较 Monte Carlo 随机组合与 PSO 最优解。
5. 读持仓：查看 `best_weights` 和 `selected_assets`。
6. 讲结论：解释收益、`volatility`、`sharpe_ratio` 和 1% 阈值。

## 3. 页面布局

- 左侧：参数控制面板。
- 顶部：项目标题和运行状态。
- 右侧 KPI：`expected_return`、`volatility`、`sharpe_ratio`、`selected_assets_count`。
- 主图区域：收敛曲线、权重分布图、风险-收益散点图。

布局目标是让答辩讲解按“参数输入 -> 优化运行 -> 收敛观察 -> baseline 对比 -> 持仓解释”的顺序自然推进。

## 4. V1 必须实现图表

1. PSO 收敛曲线。
2. 最优投资组合权重图。
3. 风险-收益散点图。
4. KPI 指标卡片。

V1 风险-收益散点图默认使用不少于 2000 个 Monte Carlo 随机组合点，并高亮 `best_point`。KPI 指标卡片必须使用统一字段名：`expected_return`、`volatility`、`sharpe_ratio`、`selected_assets_count`。

## 5. V2 可选图表

1. 夏普比率分布图。
2. 单资产风险-收益象限图。
3. PSO 搜索轨迹。
4. 15% 单票仓位上限展示。

V2 可选图表不得写入 V1 必做范围。15% 单票仓位上限仅作为扩展展示或后续约束增强，不得作为当前 V1 核心模型约束。

## 6. 原型参考说明

- 立项答辩 PPT 和 `index.html` 是视觉参考。
- 不直接照搬单文件 `index.html`。
- 正式实现必须拆成 Vue 3 组件。
- 原型中的 15% 上限只作为扩展参考，不进入 V1 核心模型。

正式前端不得依赖 CDN 版本的 Vue、Element Plus、ECharts。原型中的 ECharts 配置可以作为图表样式参考，但正式实现必须纳入 Vue 3 工程结构和项目依赖管理。

## 7. 答辩兜底方案

- 如果 UCI 数据下载失败，使用本地样例数据。
- 如果前端启动失败，使用 `python backend/run_demo.py` 输出和静态截图讲解。
- 如果后端接口失败，展示预生成 JSON 和图表截图。

兜底材料必须与冻结口径一致：连续权重、非负归一化约束、最大化 Sharpe Ratio、`volatility` 字段、1% 阈值仅用于持仓解释、Monte Carlo baseline 默认不少于 2000 个随机组合。

## 8. Demo 预设与缓存

阶段 3.5 为后续前端 Demo 增加少量预设参数和本地缓存机制，用于保证答辩演示流畅。该机制属于工程加速，不改变 PSO 算法、目标函数、约束条件或 1% 阈值解释规则。

V1 Demo 固定提供三个预设：

1. `conservative`：粒子数较少、迭代数较低，适合快速展示基础优化效果。
2. `balanced`：默认推荐预设，用于常规演示。
3. `aggressive`：粒子数和迭代数较高，用于展示更充分搜索。

缓存策略：

- 只预计算少量 Demo presets，不预计算全部参数组合。
- 用户自定义参数仍然实时计算。
- 自定义参数计算完成后可以写入本地缓存，后续相同参数请求直接返回缓存结果。
- 缓存命中通过 `cache_hit` 字段标识。
- 响应中保留 `compute_time_seconds`，用于区分真实计算耗时和缓存响应。
- 缓存文件位于 `data/cache/`，只用于本地 Demo 加速，不作为核心数据集或实验数据提交。

## 9. Web 可视化增强

系统不仅展示单次 PSO 优化结果，还支持 `conservative`、`balanced`、`aggressive` 三组预设参数对比。

新增可视化模块：

- Preset 对比图：展示三组参数下的 `expected_return`、`volatility`、`sharpe_ratio`。
- 组合权重对比图：展示不同参数设置下 Top 策略权重分布的变化。

该增强用于满足课程要求中的“展示投资组合变化、风险-收益散点图等”。其中风险-收益散点图仍由单次优化结果展示，预设对比区域用于补充说明不同 PSO 参数下组合结果的变化。
