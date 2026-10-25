"""Compare repeat runs byte-for-byte at the report serialization level."""
import json
from terraflux.pipeline import analyze
from terraflux.synthetic import make_pair


def main() -> None:
    a, b, _ = make_pair()
    first = json.dumps(analyze(a, b), sort_keys=True)
    second = json.dumps(analyze(a, b), sort_keys=True)
    assert first == second
    print("deterministic report: PASS")


if __name__ == "__main__":
    main()
