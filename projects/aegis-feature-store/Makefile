.PHONY: install test lint run seed data diagram docker

install:
	python -m pip install -e '.[dev]'

test:
	pytest -q

lint:
	ruff check src tests scripts examples

run:
	uvicorn aegis_feature_store.api:app --reload

seed:
	python scripts/seed_demo.py

data:
	python scripts/generate_data.py

diagram:
	python scripts/generate_architecture.py

docker:
	docker compose up --build
