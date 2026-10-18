"""Generate deterministic synthetic route-planning cases with reproducible seeds."""
import argparse
import json
import random
from pathlib import Path

def generate(count: int = 40, seed: int = 17) -> dict:
    rng = random.Random(seed)
    jobs = []
    for i in range(count):
        earliest = rng.randrange(480, 720, 30)
        jobs.append({"id": "J-" + str(i + 1).zfill(4),
                     "lat": round(41.07 + rng.uniform(-.09, .09), 6),
                     "lon": round(14.33 + rng.uniform(-.10, .10), 6),
                     "demand": rng.randint(1, 4), "earliest": earliest,
                     "latest": earliest + 180, "service_min": rng.randint(5, 15),
                     "priority": rng.randint(1, 3)})
    vehicles = [{"id": "van-" + str(i), "capacity": 28,
                 "shift_start": 480, "shift_end": 1080} for i in range(max(1, count // 8))]
    return {"depot": {"id": "synthetic-hub", "lat": 41.07, "lon": 14.33},
            "jobs": jobs, "vehicles": vehicles}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output", default="artifacts/synthetic_problem.json")
    args = parser.parse_args()
    if not 1 <= args.count <= 500:
        parser.error("--count must be between 1 and 500")
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(generate(args.count, args.seed), indent=2) + "\n")
    print(destination)

if __name__ == "__main__":
    main()
