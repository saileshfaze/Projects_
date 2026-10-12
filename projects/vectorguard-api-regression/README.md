# VectorGuard Semantic API Regression

Author: Sailesh (saileshfaze)

Detect REST response contract breaking changes. This repository contains a runnable reference implementation using synthetic data; it is not a deployed enterprise service.

## Run
```bash
pip install -e '.[dev]'
pytest
uvicorn app.api:app --reload
```

## License
MIT — Copyright (c) 2026 Sailesh.
