"""Generate deterministic fictional bank statements; no personal data."""
import csv
import random
from pathlib import Path

def generate(path,seed=2026,count=80):
    rng=random.Random(seed)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["day","reference","amount","memo"])
        writer.writeheader()
        for i in range(count):
            amount=rng.randint(100,20000)
            writer.writerow({"day":f"2026-10-{1+i%28:02d}","reference":f"SYN-{i:04d}",
                             "amount":amount if i%3 else -amount,"memo":f"fictional transaction {i}"})
    return path
if __name__=="__main__":
    print(generate("data/synthetic_statement.csv"))
