# Architecture

NimbusLedger uses a stateless API and pure domain functions. Ingestion adapters normalize provider records to a canonical date/provider/service/project/cost/currency schema. Cost allocation is deterministic and preserves monetary totals at cent precision. MAD-based robust z-scores flag outliers without model training. Persisted billing and authentication are future extensions; do not expose the demo API publicly without auth.
