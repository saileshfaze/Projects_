# Helios Data Contract Observatory

Author: Sailesh (saileshfaze)

Versioned schema contracts and batch data quality. This repository contains a runnable reference implementation using synthetic data; it is not a deployed enterprise service.

## Run
```bash
pip install -e '.[dev]'
pytest
uvicorn app.api:app --reload
```

## License
MIT — Copyright (c) 2026 Sailesh.
