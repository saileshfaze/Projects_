import argparse
import json
from .io import load,report
from .solver import optimize

def main():
    parser=argparse.ArgumentParser(description='Min-cost transportation optimizer')
    parser.add_argument('scenario')
    parser.add_argument('--output')
    args=parser.parse_args()
    payload=json.dumps(report(optimize(load(args.scenario))),indent=2,sort_keys=True)
    if args.output:
        from pathlib import Path
        target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(payload+'\n')
    else: print(payload)

if __name__=='__main__':main()
