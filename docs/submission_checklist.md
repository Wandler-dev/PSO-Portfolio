# 提交检查清单

## 1. 必须提交

- `backend/`
- `frontend/src/`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/vite.config.js`
- `scripts/`
- `docs/`
- `data/raw/README.md`
- `data/experiments/`
- `README.md`
- `Makefile`
- `tests/`

## 2. 不应提交

- `data/raw/*.xlsx`
- `data/cache/`
- `frontend/node_modules/`
- `frontend/dist/`
- `.run/`
- `__pycache__/`
- `.pytest_cache/`
- `.env`

## 3. 验证命令

```bash
pytest
python scripts/smoke_api.py
cd frontend && npm install && npm run build
python scripts/run_experiments.py
make demo
make status
make stop
```

## 4. 最终检查项

- `data_source = uci`。
- `asset_count = 63`。
- 实验结果文件存在。
- `docs/final_report.md` 存在。
- `docs/reproduction_guide.md` 存在。
- Web 系统可启动。
- `make stop` 能关闭服务。
- Git 工作区干净。
- 原始 Excel 未提交。

## 5. 常见风险

- 本地没有原始 Excel 时会 fallback。
- 端口 8000 或 5173 被占用。
- `frontend/node_modules/` 未安装。
- `npm run build` 可能出现 chunk size warning。
- 不能把 `cache_hit` 误解为算法没有运行。
