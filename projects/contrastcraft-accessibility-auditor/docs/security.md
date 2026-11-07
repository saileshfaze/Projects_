# Security and data handling

Offline-only parser. Never evaluate JavaScript or fetch remote assets. Treat reports as untrusted JSON if embedded elsewhere. Do not use for HTML sanitization: HTMLParser does not provide that guarantee. No telemetry or credentials.
