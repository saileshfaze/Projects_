# Vaultline — Content-Addressed Backup Lab

A reproducible engineering reference for immutable, chunk-deduplicated snapshots,
manifest integrity, restore verification, and auditable retention. Maintained as
part of the **Sailesh / saileshfaze** software portfolio.

## What it implements

- **Content-defined chunking:** deterministic 64-bit gear rolling hash with
  2 KiB minimum, 8 KiB target and 32 KiB maximum boundaries.
- **Deduplicated storage:** SHA-256 addressed chunks, atomic object replacement,
  read-time integrity checks and reuse across files/snapshots.
- **Immutable manifests:** canonical JSON plus SHA-256 checksum; per-file hashes,
  ordered chunk references, sizes, timestamps and labels.
- **Restore:** preflight integrity verification, traversal and symlink checks,
  collision refusal by default, atomic per-file replacement.
- **Retention:** dry-run prune, keep-last-N snapshots and mark/sweep orphan chunks.
- **Audit:** SQLite append-only logical chain, deterministic hash verification.
- **Interfaces:** `vaultline` CLI, optional FastAPI service and reproducible SVG
  inventory chart. All demo data is fictional and generated locally.

## Quickstart

```bash
python -m pip install -e .
python scripts/generate_fixture.py /tmp/vaultline-source --seed 42 --files 24
vaultline --vault /tmp/vaultline-store snapshot /tmp/vaultline-source --label baseline
vaultline --vault /tmp/vaultline-store list
vaultline --vault /tmp/vaultline-store stats
python scripts/demo.py
pytest -q
```

To restore, copy an `id` from `list` and run:

```bash
vaultline --vault /tmp/vaultline-store verify <snapshot-id>
vaultline --vault /tmp/vaultline-store restore <snapshot-id> /tmp/vaultline-restore
vaultline --vault /tmp/vaultline-store prune --keep 3
# Add --apply to execute pruning after reviewing the dry run.
```

## Architecture

`source files → content-defined chunks → SHA-256 object store → canonical
snapshot manifest → verified restore` with a separate SQLite audit chain.
See [architecture](docs/architecture.md), [threat model](docs/threat-model.md),
[operations](docs/operations.md) and [API](docs/api.md).

## Limitations

This is **not a production backup service**: no encryption, remote replication,
concurrent writer coordination, incremental filesystem journaling, sparse-file
support, file permissions/ACL preservation, resumable streaming, transactional
multi-file restore or resistance to a privileged attacker who can rewrite both
SQLite history and files. The source is read fully into memory per file. Symlinks
are excluded from snapshots. A SHA-256 checksum detects accidental corruption,
not a malicious attacker who can replace a manifest and its digest together.
Never use it as the sole copy of important data.

## License

MIT — Copyright (c) 2026 Sailesh.
