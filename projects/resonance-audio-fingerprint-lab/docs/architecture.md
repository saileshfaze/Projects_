# Architecture

The service is organized as independent pure-DSP, landmark, and storage modules. The decoder bounds bytes, channels, rate, and duration before allocating arrays. DSP and fingerprint extraction operate on mono floating-point samples. Fingerprints use a canonical 16 kHz sampling rate, while feature reports retain the original rate.

SQLite has `clips` (one row per unique SHA-256 WAV payload) and `landmarks` (many rows per clip, indexed by hash code). Ingest is one transaction. Search extracts query landmarks and looks up matching hash codes in batches of 250 to avoid SQLite placeholder limits. Candidate ranking uses the modal time-offset histogram, then vote count and deterministic tie-breaks.

The HTTP layer is a thin adapter around `Catalog`. A CLI and scripts reuse the same package. Audio bytes are processed in memory and not persisted; metadata and fingerprints remain until explicitly deleted.
