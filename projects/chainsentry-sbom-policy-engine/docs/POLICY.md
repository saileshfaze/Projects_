# Policy and advisory contract

## Advisory feed

```json
{"advisories": [{"id":"DEMO-1","purl_name":"pypi/example", "introduced":"0", "fixed":"2.0.0", "severity":"high", "summary":"Synthetic finding"}]}
```

Supported severities: `info`, `low`, `medium`, `high`, `critical`. A `null` fixed version means the interval is open-ended. Version comparisons use `packaging.version.Version` (PEP 440), so npm and Maven version semantics are not guaranteed. Invalid component versions do not match and must be investigated separately.

## Policy

```json
{
  "fail_at": "high",
  "deny_licenses": ["GPL-3.0-only"],
  "require_license": true,
  "require_purl": true,
  "fail_unreachable": false,
  "exemptions": [
    {"advisory": "DEMO-1", "purl": "pkg:pypi/example@1.2.0", "expires": "2027-01-01", "justification": "Temporary test-only exception"}
  ]
}
```

The threshold is inclusive. An active finding fails when its severity is at least `fail_at` and it is reachable, unless `fail_unreachable` is enabled. A valid exemption requires exact advisory ID, exact PURL, nonempty justification and expiry on or after evaluation date. This is a small VEX-inspired exception mechanism, **not** a standards-compliant VEX processor. An exception is not an assertion of non-exploitability.

License matching is case-insensitive exact-string matching. Complex SPDX expressions such as `MIT OR Apache-2.0` are not evaluated as expressions. Unknown licenses are only flagged when no license is declared and `require_license` is true.

## Interpreting the sample

The sample has six fictional components. Five are reachable from `app`. `cipherleaf` has a fictional critical advisory and `tracelog` has a denied license; both fail the default policy. `ghostcache` has a fictional high advisory but is disconnected from the application root; it remains visible as an unreachable finding. These examples are not real vulnerability claims.
