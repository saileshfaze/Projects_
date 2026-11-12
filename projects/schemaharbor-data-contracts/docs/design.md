# Design and compatibility policy

SchemaHarbor models a contract as an immutable collection of named fields. Backward compatibility means a new validator can accept records allowed by an older contract. New required fields, removed fields, narrowed types, tightened numeric ranges and disallowed nulls are breaking. Adding optional fields, widening integer to number, or relaxing bounds is compatible. A breaking change recommends a major version; a compatible change recommends minor; no changes recommend patch. These are recommendations, not automatic SemVer enforcement.

The CLI emits machine-readable JSON. `diff --fail-breaking` returns 2; `check` returns 1 for invalid rows. Impact analysis validates the dependency graph for cycles before returning a sorted transitive downstream set. Complexity is linear in the graph size plus the output set; schema comparison is approximately O(n) expected using dictionaries. Deterministic reports are intended for local demos and CI.
