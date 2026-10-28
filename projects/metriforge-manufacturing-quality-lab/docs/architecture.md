# Architecture and boundaries

```text
Synthetic CSV -> strict Reading model -> SQLite immutable event log
                                         |        |
                                         |        +-- SHA-256 chain verification
                                         v
                            QualityService (asset + lot selection)
                                         |
                         frozen baseline / production separation
                                         |
                   +---------------------+---------------------+
                   |                     |                     |
                SPC rules           capability            lot risk
                   +---------------------+---------------------+
                                         |
                          JSON report + SVG chart
                                         |
                                 CLI / REST API
```

SQLite serializes writes at database level; the event hash is computed and inserted in the same transaction. The chain detects accidental modifications but is not a cryptographic signature or tamper-proof storage against a privileged attacker. Replayed event IDs with identical payloads are ignored; conflicting replays fail. The demonstration service writes a batch one event at a time, not atomically across the batch. Production applications should use a transaction for the entire batch and apply database access controls.

Data is sorted by ISO timestamp and event ID for analysis. Only a single machine/line/metric can be evaluated together. Baseline and production must be physically distinct; selecting a baseline lot after seeing alarms biases the results.
