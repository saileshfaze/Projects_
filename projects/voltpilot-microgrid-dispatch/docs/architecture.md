# Architecture

```mermaid
flowchart LR
    A[Synthetic or JSON trace] --> B[Validation and units]
    B --> C[Dispatch policy]
    C --> D[AC energy balance and SOC checks]
    D --> E[Summary and emissions]
    E --> F[SQLite immutable run]
    D --> G[SHA-256 interval chain]
    G --> F
    E --> H[Markdown and SVG reports]
    I[CLI] --> B
    J[FastAPI] --> B
```

The simulation core is side-effect-free: given a profile, site and policy it returns a summary and interval decisions. Persistence and transport adapters live outside the core. All timestamps are timezone-aware and contiguous. SQLite records are content-addressed by configuration, summary and audit head, so repeated identical runs are idempotent.

Audit-chain verification detects accidental or malicious changes to a stored chain, but it is **not** a digital signature and cannot defend against an attacker who can rewrite the entire database and hashes. For stronger guarantees anchor the final hash externally.
