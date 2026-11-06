"""Local CLI: no network or credentials required."""
import argparse
import json
from .journal import Journal

def main(argv=None):
    parser=argparse.ArgumentParser(prog="ledgerloom")
    parser.add_argument("--db",default="ledgerloom.sqlite3")
    parser.add_argument("command",choices=["verify","trial-balance","lines","head"])
    parser.add_argument("--account")
    parser.add_argument("--through")
    args=parser.parse_args(argv)
    journal=Journal(args.db)
    result={"verify":journal.verify,"trial-balance":lambda:journal.trial_balance(args.through),
            "lines":lambda:journal.lines(args.account,args.through),"head":journal.head}[args.command]()
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if args.command!="verify" or result else 1

if __name__=="__main__":
    raise SystemExit(main())
