# LedgerLoom — Double-Entry Ledger & Reconciliation Lab

A deterministic accounting engineering reference in the **Sailesh / saileshfaze** personal portfolio. Uses synthetic transactions, integer minor units and a SQLite event journal.

## Capabilities
- Balanced double-entry posting with account types, idempotency keys, strict integer minor units and immutable journal lines.
- SHA-256 chained audit events, tamper detection, trial balances, account ledgers, and period cutoffs.
- Statement matching with exact references, amount/date tolerance and one-to-one assignment; ambiguous matches are reported for manual review.
- Reproducible synthetic statements, CLI and optional FastAPI read-only endpoints.

## Quick start
```bash
python -m pip install -e ".[dev]"
python scripts/generate_data.py
python scripts/demo.py
python -m pytest -q
python -m compileall -q src tests scripts
```
Optional API: `pip install -e ".[api]" && uvicorn ledgerloom.api:app`.

## Safety and scope
Educational prototype only. No tax, accounting or regulatory certification. No currency conversion, multi-entity consolidation, authentication, access controls or bank integration. Matching is heuristic and never posts journal entries automatically. Do not use real financial data. CI is a nested template, not automatically active at repository root. Docker and API availability depend on installed extras.
