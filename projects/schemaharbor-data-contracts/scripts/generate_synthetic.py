"""Generate fictional orders with deterministic anomalies; no external data."""
import argparse
import csv
import random
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",default="data/orders-synthetic.csv");p.add_argument("--rows",type=int,default=100);p.add_argument("--seed",type=int,default=2026)
    args=p.parse_args();rng=random.Random(args.seed)
    if not 0 <= args.rows <= 100000: raise ValueError("rows must be 0..100000")
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["order_id","amount","region"]);writer.writeheader()
        for i in range(args.rows):
            writer.writerow({"order_id":i+1,"amount":-5 if i%17==0 else rng.randrange(0,1000),"region":rng.choice(["N","S","E","W"])})
    print(f"Generated {args.rows} fictional records: {path}")
if __name__=="__main__": main()
