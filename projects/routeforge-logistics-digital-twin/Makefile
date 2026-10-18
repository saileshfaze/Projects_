install:
	python -m pip install -e ".[dev]"
test:
	python -m pytest -q
lint:
	ruff check src tests scripts
demo:
	python -m routeforge.cli data/example_problem.json --output artifacts/plan.json
serve:
	uvicorn routeforge.api:app --reload
