.PHONY: install test lint demo compare api clean
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
lint:
	ruff check src tests
demo:
	voltpilot generate --days 2 --out data/demo.json
	voltpilot run --input data/demo.json --report-dir out
compare:
	voltpilot compare --input data/demo.json
api:
	uvicorn voltpilot.api:app --reload
clean:
	rm -rf out state .pytest_cache
