# Reproducibility and synthetic data

The default seed is 42. The election timer PRNG and transport PRNG use separate seeded streams. The packet queue uses a monotonically increasing sequence number to resolve equal delivery times deterministically. No real-time sleeps or external APIs are used.

`python scripts/generate_assets.py --output out` regenerates a scenario JSON file, a JSON audit/metrics report and an SVG leadership timeline. `python scripts/verify_fixtures.py` validates the checked-in sample scenario and metrics. A stable replay must produce identical timelines and audit hashes for the same Python implementation, seed, and action list.

The scenario is fictional: five nodes, synthetic `orders` commands, and an artificial partition. Neither the dataset nor its metrics represent real infrastructure performance.
