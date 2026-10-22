PYTHON ?= python3

.PHONY: install test lint demo serve
install:
	$(PYTHON) -m pip install -e ".[dev]"
test:
	$(PYTHON) -m pytest -q
lint:
	$(PYTHON) -m ruff check src tests scripts
demo:
	$(PYTHON) scripts/generate_dataset.py --output data/generated_events.jsonl
	$(PYTHON) scripts/load_dataset.py --input data/generated_events.jsonl
serve:
	uvicorn chronos_ledger.api:app --reload
