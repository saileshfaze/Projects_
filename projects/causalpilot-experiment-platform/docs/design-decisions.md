# Design decisions

| Decision | Rationale | Tradeoff |
| --- | --- | --- |
| HMAC instead of `random` | Stable allocation across processes | Salt must remain secret and stable |
| SQLite ledger | Simple transactions, zero infrastructure | Limited write concurrency and scale |
| One final outcome per subject | Prevents accidental duplicate units | No event-sourced multi-purchase aggregation |
| CUPED with pooled theta | Simple variance-reduction baseline | Small-sample coefficient uncertainty ignored |
| Percentile bootstrap | Easy to inspect and reproduce | Not robust to heavy tails or repeated peeking |
| 2-arm-only SRM | Exact chi-square(1) survival via `erfc` | No multi-arm or stratified SRM |
| No production auth | Keeps local demo focused | Unsafe to expose without external controls |

The project emphasizes transparent, testable tradeoffs over a black-box significance verdict. A production successor would add pre-registration, exposure instrumentation, sequential-valid intervals, robust variance estimators, experiment scheduling, privacy controls, and infrastructure observability.
