# Test plan

Coverage includes WAV decoder rejection and stereo downmix; deterministic synthesis; STFT/mel dimensions and feature sanity; peak/landmark generation and time-offset voting; transactional catalog ingestion, idempotency, search, delete and persistence; REST request validation; CLI generation/analysis/search; batch error isolation; SVG generation; and SQL-injection-safe naming.

Tests use only generated audio and temporary SQLite databases. The suite does not test performance under load, compressed audio, high concurrency, adversarial WAV fuzzing, large corpora, real-world recall, or deployment behavior. Run `ruff check src tests scripts` separately if Ruff is installed.
