"""Local CPU runtime sample; results vary by host and are not performance claims."""
from __future__ import annotations
import argparse
import json
import time
from quorumcraft import Cluster


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=int, default=10000)
    args = parser.parse_args(argv)
    if not 1 <= args.ticks <= 100000:
        parser.error("ticks must be between 1 and 100000")
    cluster = Cluster(seed=42)
    start = time.perf_counter()
    cluster.tick(args.ticks)
    elapsed = time.perf_counter() - start
    print(json.dumps({"ticks": args.ticks, "elapsed_seconds": round(elapsed, 5),
                      "ticks_per_second": round(args.ticks / elapsed, 2),
                      "simulated_only": True}, indent=2))


if __name__ == "__main__":
    main()
