# Security

No live database connections, credentials or personal data are used. SQL is parsed for a restricted reference executor, not forwarded to a database. This parser is not a security control for external SQL engines. Keep .env untracked. Public deployment requires authentication, rate limits, request budgets and resource isolation.
