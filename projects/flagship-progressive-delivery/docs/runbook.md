# Runbook

From this directory:

```bash
python -m pip install -e .
python -m flagship.cli evaluate --config data/flags.json
python -m flagship.cli simulate --count 1000
python -m pip install -e '.[dev]'
python -m pytest -q
PYTHONPATH=src python scripts/generate_events.py
PYTHONPATH=src python scripts/demo.py
```

Optional API: `pip install -e '.[api]'` and `uvicorn 'flagship.api:create_app' --factory --host 127.0.0.1`. Never expose the demonstration API to untrusted networks.
