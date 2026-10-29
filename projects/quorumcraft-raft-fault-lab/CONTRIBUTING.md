# Contributing

Use Python 3.11+, install `pip install -e '.[dev]'`, run `pytest -q`, and add a deterministic regression test for every protocol change. Keep scenario inputs synthetic. Prefer explicit state transitions over hidden background timers; this simulator intentionally does not use real sockets or threads. Open changes as small, reviewable commits with a description of the safety property being preserved. Do not add secrets or private network captures.
