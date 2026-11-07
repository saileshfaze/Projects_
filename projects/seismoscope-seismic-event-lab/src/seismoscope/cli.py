"""Command line entrypoint."""
import argparse,json
from pathlib import Path
from .pipeline import run

def main():
    parser=argparse.ArgumentParser(description='Synthetic seismic arrival analysis')
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=json.dumps(run(args.seed),indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(report+'\n')
    else:print(report)
if __name__=='__main__':main()
