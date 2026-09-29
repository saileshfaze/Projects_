.PHONY: install test lint run data
install:
	pip install -e ".[dev]"
test:
	pytest
lint:
	ruff check app tests scripts
run:
	uvicorn app.main:app --reload
data:
	python scripts/generate_dataset.py
