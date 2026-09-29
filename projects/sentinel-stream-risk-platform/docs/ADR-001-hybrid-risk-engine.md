# ADR-001: Hybrid rules and anomaly detection

Status: Accepted

## Context
Pure rules are explainable but brittle; pure anomaly models can be opaque and unstable under drift.

## Decision
Blend an Isolation Forest anomaly signal with deterministic behavioral rules and emit reason codes. Thresholds remain configuration.

## Consequences
Calibration here is illustrative. Production requires labeled validation, fairness analysis, drift monitoring, and formal model governance.
