# Flagship — Progressive Delivery & Experimentation Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT licensed · Python 3.10+

An engineering portfolio reference for deterministic feature flags, progressive rollouts, rule-based targeting, and descriptive experiment reporting. Built with synthetic data; not a commercial service or production experiment platform.

## Capabilities

- Stable SHA-256 subject bucketing and weighted allocations in 10,000 basis points
- Ordered targeting rules, disabled flag fallbacks, configuration validation
- Deduplicated exposure/conversion summaries and Wilson confidence intervals
- Append-only local JSONL hash-chain demonstration
- CLI, optional FastAPI endpoint, deterministic event generator and pytest suite
- Docker/Compose development configuration and an inactive CI workflow template

## Quick start

```bash
python -m pip install -e .
python -m flagship.cli evaluate
python -m flagship.cli simulate --count 1000 --seed 42
python -m pip install -e '.[dev]'
python -m pytest -q
```

Read [architecture](docs/architecture.md) and [runbook](docs/runbook.md). The example treatment probabilities are fictional and cannot establish treatment effects. No secrets, actual users or personal data are included.
