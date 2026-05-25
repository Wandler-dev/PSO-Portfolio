# PSO Portfolio Dashboard

基于粒子群优化算法的投资组合风险-收益均衡决策系统。当前版本包含 FastAPI 后端和 Vue 3 + ECharts 前端看板。

## 环境准备

项目提供 `environment.yml`，推荐使用 conda/mamba 创建独立环境：

```bash
conda env create -f environment.yml
conda activate portfolio-pso
```

如果环境已经存在，可更新依赖：

```bash
conda env update -f environment.yml --prune
conda activate portfolio-pso
```

当前项目不要求安装全局系统包，也不需要修改 `base` 环境。

## 快速启动 Web 系统

推荐方式：

```bash
make demo
```

然后浏览器打开：

```text
http://127.0.0.1:5173
```

停止服务：

```bash
make stop
```

查看状态：

```bash
make status
```

关闭浏览器标签页不会停止后端和前端服务。再次运行 `make demo` 时，如果服务已经在运行，脚本会直接输出访问地址；如果需要释放端口，请先执行：

```bash
make stop
```

如果没有 `make`，也可以使用：

```bash
bash scripts/start_demo.sh
bash scripts/stop_demo.sh
bash scripts/status_demo.sh
```

## 后端启动

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

常用验证：

```bash
pytest
python scripts/smoke_api.py
```

## 前端启动

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

前端通过 Vite proxy 将 `/api` 转发到 `http://127.0.0.1:8000`。使用前请先启动后端。

构建检查：

```bash
cd frontend
npm run build
```

## 实验材料生成

阶段五 A 的实验结果和分析材料可通过以下命令生成：

```bash
python scripts/run_experiments.py
```

脚本会输出 `data/experiments/experiment_summary.json`、`data/experiments/experiment_summary.csv` 和 `data/experiments/convergence_curves.json`，用于课程报告引用。

## 项目文档索引

- `docs/final_report.md`：最终课程项目报告正文草稿。
- `docs/experiment_results.md`：实验结果与分析。
- `docs/reproduction_guide.md`：复现与运行说明。
- `docs/submission_checklist.md`：最终提交检查清单。

## Git 提交约定

以下内容不提交 Git：

- `data/raw/*.xlsx`
- `data/cache/`
- `frontend/node_modules/`
- `frontend/dist/`

## 系统使用流程

1. 启动 FastAPI 后端。
2. 启动 Vue 前端。
3. 在左侧选择 `conservative`、`balanced` 或 `aggressive` 预设，或手动调整 PSO 参数。
4. 点击“开始优化”。
5. 查看 KPI、PSO 收敛曲线、权重 Top 10、风险-收益散点图和入选策略表格。
