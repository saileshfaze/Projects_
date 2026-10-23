.PHONY: install test lint data bench run diagram
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
lint:
	ruff check src tests scripts
data:
	python scripts/generate_data.py
bench:
	python scripts/run_benchmark.py
run:
	uvicorn verityrag.api:app --reload
diagram:
	python scripts/generate_diagram.py
