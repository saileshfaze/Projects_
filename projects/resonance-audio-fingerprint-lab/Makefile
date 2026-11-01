.PHONY: test demo fixtures api lint

test:
	python -m pytest -q

fixtures:
	python scripts/generate_fixtures.py

demo:
	python scripts/demo.py

api:
	uvicorn resonance.api:app --reload

lint:
	ruff check src tests scripts
