.PHONY: install test demo check diagram serve
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
demo:
	python scripts/demo.py
check:
	python scripts/check_determinism.py
diagram:
	python scripts/architecture.py
serve:
	uvicorn terraflux.api:app --host 127.0.0.1 --port 8000
