# Security and privacy

WAV ingestion enforces file size, duration, sample-rate, channel and integer-PCM restrictions. The service accepts base64 WAV and does not invoke shell commands or remote APIs. Database statements use parameters for values. Search query batching builds placeholder strings from a bounded count, never from user-supplied SQL. Raw WAV bytes are not written to SQLite.

This demo intentionally omits authentication, authorization, per-client quotas, TLS, malware scanning, and storage encryption. It must not be internet-exposed as-is. Fingerprint hashes can disclose information about source audio if compared against a known catalog. Treat catalog files as potentially sensitive, use restrictive file permissions, and delete them when no longer needed.

Do not commit `.env`, API keys, recordings, or private datasets. The `.env.example` contains no secrets. Docker binds to 127.0.0.1 and uses an unprivileged runtime user.
