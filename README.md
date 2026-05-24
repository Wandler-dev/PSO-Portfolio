# PSO Portfolio Dashboard

基于粒子群优化算法的投资组合风险-收益均衡决策系统。当前版本包含 FastAPI 后端和 Vue 3 + ECharts 前端看板。

## 后端启动

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
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
npm run dev
```

前端通过 Vite proxy 将 `/api` 转发到 `http://127.0.0.1:8000`。使用前请先启动后端。

构建检查：

```bash
cd frontend
npm run build
```

## Git 提交约定

以下内容不提交 Git：

- `data/raw/*.xlsx`
- `data/cache/`
- `frontend/node_modules/`
- `frontend/dist/`

## Demo 流程

1. 启动 FastAPI 后端。
2. 启动 Vue 前端。
3. 在左侧选择 `conservative`、`balanced` 或 `aggressive` 预设，或手动调整 PSO 参数。
4. 点击“开始优化”。
5. 查看 KPI、PSO 收敛曲线、权重 Top 10、风险-收益散点图和入选策略表格。
