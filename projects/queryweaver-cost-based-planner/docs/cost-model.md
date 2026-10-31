# Cost model

Equality filter selectivity is 1 / distinct_count; inequality is 1 - 1 / distinct_count. Numeric ranges use a uniform minimum-to-maximum estimate; other ranges fall back to 0.3333. Join selectivity is 1 / max(distinct_left, distinct_right). Filter independence is assumed.

Table scan cost: base_rows + 0.1 * filtered_rows. Modeled index scan: log2(base_rows + 1) + 1.5 * filtered_rows. Nested-loop join: left.cost + right.cost + left.rows * max(1, right.rows). Hash join: left.cost + right.cost + 1.2 * (left.rows + right.rows) + 0.1 * output_rows. Indexed nested-loop estimates per-left-row logarithmic lookups and matches.

These are abstract cost units, not seconds or disk I/O. No memory spills, skew, correlations, cache effects, network transfer, bushy plans or actual B-tree execution are modeled.
