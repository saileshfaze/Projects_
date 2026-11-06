# Threat model and limitations

The hash chain detects accidental or unsophisticated tampering if the expected head hash is trusted externally; an attacker able to rewrite all records and the trusted head can forge history. SQLite does not provide multi-host coordination or hardened authorization. The local prototype assumes a trusted operator and one currency per journal. Ambiguous statement matches are not resolved automatically. No banking credentials or personal information are required.
