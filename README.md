# Portfolio PSO Dashboard

基于粒子群优化算法（Particle Swarm Optimization, PSO）的投资组合风险-收益均衡决策系统。项目包含手写 PSO 优化器、UCI 数据集解析、Monte Carlo 随机组合基准、FastAPI 后端、Vue 3 + ECharts Web 可视化界面，以及可复现实验脚本。

GitHub 仓库：<https://github.com/Wandler-dev/PSO-Portfolio>

本项目是课程实验与可视化系统，不是实盘交易系统，不包含券商接口、自动下单或投资建议功能。

## 功能特性

- 手写 PSO 连续权重优化，不使用 `scipy.optimize`、`pyswarms` 等黑盒优化库。
- 投资组合权重满足 `wi >= 0` 且 `sum(wi) = 1`。
- 目标函数为最大化夏普比率（Sharpe Ratio）。
- 使用 UCI Stock Portfolio Performance 数据集，并提供模拟数据 fallback。
- 使用 Monte Carlo 随机组合生成风险-收益散点基准。
- FastAPI 提供健康检查、数据摘要、预设参数和优化接口。
- Vue 3 + Element Plus + ECharts 提供 Web 可视化界面。
- 支持 conservative、balanced、aggressive 三组预设参数对比。
- 提供实验脚本与已生成实验结果，便于复现报告中的分析。

## 项目结构

```text
backend/
  app/
    data_loader.py        # UCI 数据解析与 fallback
    portfolio_math.py     # 收益、波动率、Sharpe Ratio 计算
    pso_optimizer.py      # 手写 PSO 优化器
    random_baseline.py    # Monte Carlo 随机组合基准
    main.py               # FastAPI 应用入口
    services.py           # API 业务编排
frontend/
  src/                    # Vue 3 + ECharts 前端看板
scripts/
  start_demo.sh           # 启动后端 + 前端
  stop_demo.sh            # 停止本项目启动的服务
  smoke_api.py            # API smoke test
  run_experiments.py      # 实验结果生成脚本
data/
  raw/                    # UCI 原始数据与说明
  experiments/            # 可复现实验结果
docs/                     # 公开项目文档
tests/                    # pytest 测试
```

## 数据集

仓库包含课程使用的数据文件：

```text
data/raw/stock portfolio performance data set.xlsx
```

该数据来自 UCI Stock Portfolio Performance 数据集。它不是 `date / symbol / close` 格式的原始股票价格时间序列，而是 weighted scoring stock portfolios 的表现数据。本项目将数据中的每个 ID 解释为一个候选选股权重策略（candidate stock-selection weighting strategy），PSO 优化的是这些候选策略之间的资金分配权重。

当前实现中：

- `expected_returns` 优先来自 `all period` 表中的 `original Annual Return`。
- `covariance_matrix` 由 `1st / 2nd / 3rd / 4th period` 的 Annual Return observations 构造。
- Annual Return 已是绩效指标，因此不进行 252 个交易日年化。
- 如果原始数据缺失或解析失败，系统会使用 `simulated_fallback`，并在 API 响应中明确标注。

更多说明见 [data/raw/README.md](data/raw/README.md) 和 [docs/DATA_SPEC.md](docs/DATA_SPEC.md)。

## 环境准备

推荐使用 conda 或 mamba 创建独立环境：

```bash
conda env create -f environment.yml
conda activate portfolio-pso
```

如果环境已经存在，可更新依赖：

```bash
conda env update -f environment.yml --prune
conda activate portfolio-pso
```

项目不要求安装全局系统包，也不需要修改 `base` 环境。`environment.yml` 已包含 Python、FastAPI、NumPy、Pandas、openpyxl、pytest 和 Node.js。

## 快速启动

启动完整 Web 系统：

```bash
make demo
```

浏览器打开：

```text
http://127.0.0.1:5173
```

查看运行状态：

```bash
make status
```

停止后端和前端服务：

```bash
make stop
```

关闭浏览器标签页不会停止后端和前端服务。再次运行 `make demo` 时，如果服务已经在运行，脚本会直接输出访问地址；如果需要释放端口，请执行 `make stop`。

没有 `make` 时可直接运行脚本：

```bash
bash scripts/start_demo.sh
bash scripts/status_demo.sh
bash scripts/stop_demo.sh
```

## 手动运行

启动后端：

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

启动前端：

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

前端通过 Vite proxy 将 `/api` 转发到 `http://127.0.0.1:8000`。

## API

主要接口：

- `GET /api/health`：后端健康检查。
- `GET /api/data/summary`：数据源、候选策略数量、年化状态和数据说明。
- `GET /api/presets`：返回 conservative、balanced、aggressive 三组预设参数。
- `POST /api/optimize`：运行 PSO 优化并返回 KPI、最优权重、收敛曲线、Monte Carlo 随机组合点和入选策略表。

字段命名遵守 [docs/API_CONTRACT.md](docs/API_CONTRACT.md)，对外统一使用 `expected_return`、`volatility`、`sharpe_ratio`、`best_weights`、`selected_assets` 等字段。

## 运行测试

后端测试：

```bash
pytest
```

API smoke test：

```bash
python scripts/smoke_api.py
```

前端构建：

```bash
cd frontend
npm install
npm run build
```

也可以使用 Makefile：

```bash
make test
make smoke
make frontend-build
```

## 复现实验

运行实验脚本：

```bash
python scripts/run_experiments.py
```

脚本会基于当前数据源运行多组 PSO 参数实验，并输出：

```text
data/experiments/experiment_summary.json
data/experiments/experiment_summary.csv
data/experiments/convergence_curves.json
```

已生成的实验结果随仓库一起提供，可直接用于核对报告中的实验分析。实验说明见 [data/experiments/README.md](data/experiments/README.md) 和 [docs/experiment_results.md](docs/experiment_results.md)。

## Web 界面

Web 界面支持：

- 后端连接状态和数据集摘要。
- PSO 参数控制与三组预设参数。
- KPI 指标：期望收益率（Expected Return）、波动率（Volatility）、夏普比率（Sharpe Ratio）、入选策略数、缓存状态和计算耗时。
- PSO 收敛曲线。
- 最优组合权重 Top 10。
- 风险-收益散点图：Monte Carlo 随机组合 vs PSO 最优解。
- 入选策略表。
- 三组预设参数的指标对比和组合权重对比。

## 文档

公开文档：

- [docs/final_report.md](docs/final_report.md)：课程项目报告正文。
- [docs/experiment_results.md](docs/experiment_results.md)：实验结果与分析。
- [docs/reproduction_guide.md](docs/reproduction_guide.md)：复现与运行说明。
- [docs/submission_checklist.md](docs/submission_checklist.md)：提交检查清单。
- [docs/API_CONTRACT.md](docs/API_CONTRACT.md)：API 数据契约。
- [docs/DATA_SPEC.md](docs/DATA_SPEC.md)：数据规范。
- [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)：项目计划。
- [docs/uci_dataset_profile.md](docs/uci_dataset_profile.md)：UCI Excel 数据画像。

内部开发过程文档、Codex 指令和答辩草稿不作为公开 GitHub 材料追踪。

## 限制与说明

- PSO 是启发式算法，不保证数学意义上的全局最优。
- UCI 数据不是原始股票价格序列，协方差矩阵由有限 period observations 构造，存在低秩和估计不稳定的局限。
- Monte Carlo baseline 是随机组合基准，不是理论最优解。
- `cache_hit` 只表示工程缓存命中，不改变算法定义或实验结果真实性。
- 当前系统未考虑交易成本、调仓频率、行业约束、流动性约束等真实投资限制。
- 本项目不提供投资建议，不应用于实盘交易。

## Git 跟踪策略

仓库追踪：

- 源码、测试、脚本、环境文件和 Makefile。
- UCI 原始 Excel 数据文件。
- 可复现实验结果。
- 面向协作者的公开文档。

仓库不追踪：

- `data/cache/`
- `frontend/node_modules/`
- `frontend/dist/`
- `.run/`
- `__pycache__/`
- `.pytest_cache/`
- `.env`

## License

当前仓库尚未指定开源许可证。如需正式公开发布，请在发布前补充 `LICENSE` 文件。
