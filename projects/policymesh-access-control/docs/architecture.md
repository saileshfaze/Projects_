# Architecture

Input request and versioned policy JSON are validated, then each rule is matched against action and resource glob patterns and its conjunctive attribute predicates. Matching rules are recorded in original policy order. Decision combining is **deny-overrides**, then allow, then implicit default deny. Canonical JSON serialization produces deterministic batch output. No network calls or persistence occur.

The evaluator is intentionally simple enough for inspection and extension. Rule matching is linear in rule count; it is not optimized for large policy sets.
