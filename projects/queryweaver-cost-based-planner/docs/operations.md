# Operations

Python 3.11+ is required. Install API/test extras with python -m pip install -e '.[api,dev]'. Run python -m pytest -q and python scripts/check_invariants.py --seeds 30. Rebuild fixtures with python scripts/generate_data.py --out data --seed 2026 and diagrams with python scripts/build_assets.py. Run the benchmark with python scripts/run_benchmark.py --out out/benchmark.json.

Start the optional API using uvicorn queryweaver.api:app --host 127.0.0.1 --port 8000. Docker requires dependency downloads at build time. The Compose service binds to localhost, runs non-root and uses a read-only filesystem.

To activate CI, deliberately copy the nested project workflow into repository-root .github/workflows/queryweaver-ci.yml. Nested templates are not executed automatically.
