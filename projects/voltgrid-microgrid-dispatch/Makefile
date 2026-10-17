.PHONY: install test lint serve generate docker
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest
lint:
	ruff check src tests scripts
serve:
	uvicorn voltgrid.api:app --reload --host 127.0.0.1
generate:
	python scripts/generate_scenarios.py
	python scripts/generate_architecture.py
docker:
	docker compose up --build
