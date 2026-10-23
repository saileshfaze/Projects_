# Threat model

**Untrusted inputs:** document bodies, titles, query strings and evaluation payloads. The system does not call external tools or an LLM, so instruction text inside documents is treated as inert data. A regex blocks a few recognizable instruction attacks at answer time. This is *not* comprehensive prompt-injection protection; it can cause false positives and misses indirect attacks.

**Data handling:** answer text masks basic email and telephone patterns. This is not full PII detection and does not redact search results, stored documents, or logs. Never ingest sensitive customer documents without separate access controls and a retention policy.

**API exposure:** there is no authentication, authorization, per-tenant isolation, request rate limit, encryption-at-rest, or audit-log access control. Bind only to localhost in development. The Docker container uses a non-root user, read-only root filesystem and a writable named volume.

**Evaluation integrity:** synthetic qrels are trusted local fixtures. Results can be gamed by tuning on this tiny dataset; hold out independent test questions for real evaluation. No dependency vulnerability scanning or deployment security review is claimed.
