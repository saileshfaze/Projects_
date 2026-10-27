"""Validate input and demonstrate trace statistics."""
import argparse
from voltpilot.synthetic import load_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument("path")
    args=parser.parse_args()
    rows=load_json(args.path)
    print(f"{len(rows)} intervals; peak load {max(x.load_kw for x in rows):.2f} kW; outages {sum(not x.grid_available for x in rows)}")


if __name__=="__main__": main()
