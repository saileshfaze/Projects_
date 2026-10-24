.PHONY: install test lint demo serve diagram
install:
	python -m pip install -e '.[api,dev]'
test:
	python -m pytest
lint:
	ruff check src tests
demo:
	python scripts/run_demo.py
serve:
	uvicorn causalpilot.api:app --reload
diagram:
	python scripts/generate_diagram.py
