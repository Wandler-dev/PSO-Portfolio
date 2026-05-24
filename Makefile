.PHONY: demo stop status test smoke frontend-build clean

demo:
	bash scripts/start_demo.sh

stop:
	bash scripts/stop_demo.sh

status:
	bash scripts/status_demo.sh

test:
	pytest

smoke:
	python scripts/smoke_api.py

frontend-build:
	cd frontend && npm install && npm run build

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache frontend/dist .run
