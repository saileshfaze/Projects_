.PHONY: install test lint serve demo assets pdf docker
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
lint:
	ruff check app tests
serve:
	uvicorn app.api:app --reload
demo:
	python scripts/generate_synthetic.py
	python -m app.cli data/baseline_orders.json data/candidate_orders.json --output reports/evaluation.json
assets:
	python scripts/generate_assets.py
pdf:
	python scripts/generate_report.py reports/evaluation.json reports/evaluation.pdf
docker:
	docker compose up --build
