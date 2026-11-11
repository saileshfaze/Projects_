# PacketForge — Framed Protocol Robustness Lab

A portfolio-grade, deterministic protocol engineering reference by **Sailesh / saileshfaze**. Demonstrates byte-level serialization, CRC32 integrity checks, incremental stream decoding, reproducible mutation campaigns, structured traces, CLI, and optional FastAPI.

## Quick start

```bash
python -m pip install -e .
python -m pytest -q
packetforge encode hello --sequence 7
packetforge campaign --seed 2026 --cases 500
python scripts/generate_fixtures.py
python scripts/run_demo.py
```

## Scope and limitations

PF/1 is an invented laboratory protocol. The mutation campaign does **not** target live services and does not prove security or protocol compliance. CRC32 is not authentication. The optional API is not production hardened. Synthetic traces are deterministic and contain no customer data. This is a portfolio implementation, not independently validated research. See `docs/` for protocol specification, architecture, and testing. MIT licensed, Copyright (c) 2026 Sailesh.
