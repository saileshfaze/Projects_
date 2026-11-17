# Policy contract

A policy contains a nonempty `version` and a `rules` array. Each rule requires a unique `id`, an `effect` of `allow` or `deny`, nonempty arrays of `actions` and `resources` using shell-style wildcard patterns, and an optional `when` array. Predicates are conjunctive and have `path` (dot-separated starting with `subject`, `environment`, or `resource_attributes`), `op`, and `value`. Supported operators: `eq`, `ne`, `in`, `not_in`, `gte`, `lte`, `contains`, `exists`. Missing attributes do not match except `exists: false`. `gte`/`lte` require numeric operands and exclude booleans.

Requests contain `action`, `resource`, `subject` object, and optional `environment` and `resource_attributes` objects. Caller is responsible for authenticating subjects and providing truthful attributes. Rule patterns are case-sensitive.
