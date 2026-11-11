# Architecture

PF/1 is an invented demonstration protocol, not an Internet standard. The codec validates length, version, magic and CRC32 before yielding immutable `Frame` records. A streaming parser accepts fragmented input and optionally skips corrupt bytes. The seeded mutator exercises truncation, bit flips, insertion, duplication and byte zeroing. The campaign classifies rejected versus accepted mutations; an accepted mutation is **not** evidence of a vulnerability. JSON traces contain only generated payloads.

## Threat model

The decoder rejects malformed frames but is not a cryptographic authentication scheme. CRC32 detects accidental corruption, not malicious tampering. The API has no authentication or rate limiting. Run locally only; the container demo disables networking.
