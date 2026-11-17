# PolicyMesh — Attribute-Based Access Control Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · 2026

A deterministic, offline policy-as-code evaluation engine demonstrating deny-overrides ABAC, default-deny, wildcard action/resource matching, typed attribute predicates, traceable matched rule IDs, and reproducible fictional authorization workloads.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
policymesh data/policy.json data/requests.json --output artifacts/decisions.json
python scripts/generate.py --seed 2026 --count 100 --output artifacts/generated.json
policymesh data/policy.json artifacts/generated.json
```

## Scope

The evaluator accepts trusted local JSON policy documents and request batches. Explicit deny overrides allow regardless of rule order. Otherwise, any matching allow grants access; unmatched requests deny by default. The decision includes all matched rule IDs for debugging.

This is **not** a production authorization gateway: it lacks signed policies, policy provenance, sandboxing for untrusted inputs, tenancy isolation, identity verification, distributed cache invalidation, enforcement integration, or formal verification. Do not use it to protect real systems. All sample identities are fictional.

See [architecture](docs/architecture.md), [contract](docs/policy-contract.md), and [limitations](docs/limitations.md).
