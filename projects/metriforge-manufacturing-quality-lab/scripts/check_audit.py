"""Verify the SQLite event hash chain."""
import argparse,json
from metriforge.service import QualityService

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db',default='state/demo.sqlite');args=parser.parse_args()
    result=QualityService(args.db).audit();print(json.dumps(result,indent=2,sort_keys=True))
    if not result['valid']:raise SystemExit(1)
if __name__=='__main__':main()
