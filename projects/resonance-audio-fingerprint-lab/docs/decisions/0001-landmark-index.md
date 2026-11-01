# ADR 0001: Deterministic landmark index

**Decision:** Use STFT peak-pair hashes and a SQLite inverted index instead of a neural audio embedding model.

**Reasons:** Offline operation, explainability, reproducibility, compact dependencies and clear failure modes.

**Trade-offs:** Sensitivity to time stretching, pitch shifts, masking noise and sparse content. The retrieval score is a heuristic, not calibrated. Production applications should evaluate robustness on licensed representative data and compare against alternative retrieval baselines.
