.PHONY: test lint demo fixtures serve

test:
	pytest -q

lint:
	ruff check src tests scripts

demo:
	python scripts/demo.py

fixtures:
	python scripts/generate_fixtures.py
	python scripts/render_architecture.py

serve:
	uvicorn chainsentry.api:app --host 127.0.0.1 --port 8000
