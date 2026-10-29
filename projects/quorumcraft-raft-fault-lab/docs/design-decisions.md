# Design decisions

**Discrete-event over real sockets:** stable reproducibility, easy fault injection and no dependence on wall-clock timing.

**Python standard library for the protocol core:** straightforward inspection of state transitions. FastAPI is isolated in the adapter.

**No third-party consensus library:** the educational objective is to implement and test the algorithmic rules, not to claim production robustness.

**Separate audit chain and protocol log:** the audit trace records simulator actions; it is not a Raft consensus log and must not be confused with one.

**SVG instead of charting framework:** small, portable generated asset, reviewable in a pull request.

**Project-local CI template:** keeps this project self-contained inside a multi-project repository; activation requires a deliberate root-level workflow change.
