# Test strategy

Run `pip install -e '.[dev]'` and `pytest -q` from this project directory. Tests cover both SBOM adapters, malformed inputs, graph reachability and cycles, PURL matching, version boundaries, exemption expiry, policy decisions, stable inventory digests, SQLite persistence, drift, CLI exit codes, HTTP endpoints, and deterministic fixture generation.

The synthetic feed contains deliberately invented advisories. A passing test suite proves that the documented behaviors work on those fixtures; it does not validate vulnerability-detection accuracy on real packages.

Additional checks:

```bash
python -m compileall -q src tests scripts
python scripts/check_reproducibility.py
python scripts/demo.py
# If Ruff is installed:
ruff check src tests scripts
```

Docker image execution and remote CI are separate from local unit testing. A nested workflow template is included but will not run until moved to the repository-root workflow directory.
