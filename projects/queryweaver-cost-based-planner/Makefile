.PHONY: install test demo data benchmark invariants assets api
install:
	python -m pip install -e '.[api,dev]'
test:
	python -m pytest -q
demo:
	python -m queryweaver --execute
data:
	python scripts/generate_data.py
benchmark:
	python scripts/run_benchmark.py
invariants:
	python scripts/check_invariants.py --seeds 30
assets:
	python scripts/build_assets.py
api:
	uvicorn queryweaver.api:app --reload
