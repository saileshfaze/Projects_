.PHONY: install test demo api lint
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
lint:
	ruff check src tests scripts
demo:
	python scripts/generate_scenarios.py
	python -m skyweave data/crossing.json --out out --samples 100
api:
	uvicorn skyweave.api:app --reload
