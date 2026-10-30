"""Verify local SQLite snapshots and their audit hash chain."""
import argparse
from skyweave.persistence import Store

p=argparse.ArgumentParser();p.add_argument('database')
args=p.parse_args()
valid=Store(args.database).verify()
print('Audit chain:', 'valid' if valid else 'INVALID')
raise SystemExit(0 if valid else 1)
