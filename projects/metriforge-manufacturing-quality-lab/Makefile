.PHONY: install test lint demo api clean
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
lint:
	ruff check src tests scripts
demo:
	python scripts/run_demo.py
api:
	uvicorn metriforge.api:app --host 127.0.0.1 --port 8080
clean:
	rm -rf state reports
