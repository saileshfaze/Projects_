.PHONY: install test lint demo generate stress docker
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
lint:
	ruff check src tests scripts
demo:
	quorumcraft demo --output out/demo.json --svg out/timeline.svg
generate:
	python scripts/generate_assets.py --output out
stress:
	python scripts/stress_matrix.py --seeds 100
docker:
	docker compose up --build
