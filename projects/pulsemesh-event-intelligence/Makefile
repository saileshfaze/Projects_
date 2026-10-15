.PHONY: install test lint run demo assets
install:
	python -m pip install -e ".[dev]"
test:
	pytest -q
lint:
	ruff check src tests scripts
run:
	uvicorn pulsemesh.api:app --reload
demo:
	python scripts/migrate.py
	python scripts/generate_dataset.py
	pulsemesh load data/synthetic_events.jsonl
assets:
	python scripts/generate_assets.py
