.PHONY: test compile demo fixtures benchmark

test:
	PYTHONPATH=src python -m pytest -q
compile:
	python -m compileall -q src tests scripts
demo:
	PYTHONPATH=src python scripts/demo.py
fixtures:
	PYTHONPATH=src python scripts/generate_fixture.py sample-output/source
benchmark:
	PYTHONPATH=src python scripts/benchmark.py
