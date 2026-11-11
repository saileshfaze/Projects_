# PF/1 wire format

| Field | Width | Encoding |
|---|---:|---|
| Magic | 2 bytes | ASCII `PF` |
| Version | 1 byte | unsigned, fixed `1` |
| Kind | 1 byte | unsigned |
| Sequence | 4 bytes | unsigned big-endian |
| Payload length | 2 bytes | unsigned big-endian, max 4096 |
| Payload | variable | uninterpreted bytes |
| Checksum | 4 bytes | CRC32 over all preceding bytes, big-endian |

Strict decoder rejects trailing bytes, unknown versions, invalid sizes, wrong checksums and truncated messages. The stream decoder can optionally resynchronize by skipping one byte on corruption; this is a best-effort teaching behavior and may misidentify accidental magic sequences.
