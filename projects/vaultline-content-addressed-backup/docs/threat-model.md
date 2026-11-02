# Threat model and limitations

## Covered

- Accidental corruption of an object: SHA-256 verified on every read.
- Accidental manifest modification: canonical checksum checked before use.
- Unsafe manifest paths: absolute, traversal, empty and backslash paths rejected.
- Existing restore destination files: refused unless `overwrite=True`.
- Source symlinks: excluded from snapshot traversal.
- Simple audit-row mutation: chained SHA-256 detects modification or deletion.

## Not covered

- Malicious actors with write access to the entire vault: no keyed signatures.
- Symlink race / TOCTOU by concurrent hostile processes during restore.
- Arbitrary untrusted input size or decompression bombs (there is no compression).
- Encryption at rest, authenticated remote transport, retention locks.
- Consistent snapshots of concurrently modified files; no filesystem freeze.
- Metadata fidelity: timestamps, modes, hardlinks, ACLs, ownership not restored.
- A complete atomic restore of multiple files; each file is replaced atomically.
- Network access authentication; do not expose the sample API publicly.

For real backups, use an audited tool with encryption, remote copies, access
controls, integrity monitoring and regular restore drills.
