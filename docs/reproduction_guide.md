# 复现与运行说明

## 1. 环境准备

项目需要 Python 后端环境和 Node 前端环境。

Python 环境应包含：

- Python 3.11
- NumPy
- Pandas
- FastAPI
- Uvicorn
- openpyxl
- pytest

前端环境应包含：

- Node.js
- npm

前端依赖通过本地 npm 安装，不使用 CDN：

```bash
cd frontend
npm install
cd ..
```

UCI 原始 Excel 文件应放在 `data/raw/` 下，推荐文件名：

```text
data/raw/stock portfolio performance data set.xlsx
```

或：

```text
data/raw/uci_stock_portfolio_performance.xlsx
```

原始 Excel 文件不提交 Git。若本地没有原始 Excel，数据加载器会 fallback 到模拟数据，并在 `data_source` 和 `source_notes` 中说明。

## 2. 后端测试

运行单元测试：

```bash
pytest
```

运行 API smoke test：

```bash
python scripts/smoke_api.py
```

该脚本会临时启动后端服务，检查 health、data summary、presets 和 optimize 接口。某些受限沙箱环境可能禁止访问 `127.0.0.1`，此时需要按当前环境权限重新验证。

## 3. 运行实验

生成实验结果：

```bash
python scripts/run_experiments.py
```

输出文件：

- `data/experiments/experiment_summary.json`
- `data/experiments/experiment_summary.csv`
- `data/experiments/convergence_curves.json`

这些文件用于最终课程报告中的实验结果表格和分析。若 `data_source` 不是 `uci`，实验结果不能作为真实 UCI 数据结果使用。

## 4. 启动 Web 系统

推荐使用 Makefile：

```bash
make demo
make status
make stop
```

启动后访问：

```text
http://127.0.0.1:5173
```

如果没有 `make`，可直接运行脚本：

```bash
bash scripts/start_demo.sh
bash scripts/status_demo.sh
bash scripts/stop_demo.sh
```

启动脚本会将后端和前端进程写入 `.run/` 下的 pid 文件，并将日志写入 `.run/backend.log` 和 `.run/frontend.log`。

## 5. 前端构建

```bash
cd frontend
npm install
npm run build
cd ..
```

构建产物位于 `frontend/dist/`，该目录不提交 Git。当前前端依赖包含 Element Plus 和 ECharts，构建时可能出现 chunk size warning，这不影响构建是否通过。

## 6. 注意事项

- `data/raw/*.xlsx` 不提交 Git。
- `data/cache/` 不提交 Git。
- `frontend/node_modules/` 不提交 Git。
- `frontend/dist/` 不提交 Git。
- `.run/` 不提交 Git。
- 普通沙箱可能限制 localhost 访问或端口绑定，需要按环境权限验证。
- `cache_hit` 表示缓存命中，不影响算法结果真实性。
- 1% 权重阈值只用于解释 `selected_assets`，不参与优化约束。
