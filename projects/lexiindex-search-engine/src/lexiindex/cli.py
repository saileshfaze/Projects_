import argparse
import json
from .core import Index

def main():
    p=argparse.ArgumentParser(description='Offline SQLite inverted index')
    p.add_argument('--db',default='lexiindex.sqlite3')
    sub=p.add_subparsers(dest='command',required=True)
    add=sub.add_parser('ingest');add.add_argument('jsonl')
    q=sub.add_parser('search');q.add_argument('query');q.add_argument('--phrase',action='store_true');q.add_argument('--limit',type=int,default=10)
    sub.add_parser('stats')
    rm=sub.add_parser('delete');rm.add_argument('id')
    a=p.parse_args();idx=Index(a.db)
    try:
        if a.command=='ingest':
            count=0
            with open(a.jsonl,encoding='utf-8') as stream:
                for line in stream:
                    if not line.strip():continue
                    doc=json.loads(line);idx.upsert(doc['id'],doc['title'],doc['body']);count+=1
            print(json.dumps({'ingested':count,'stats':idx.stats()}))
        elif a.command=='search':print(json.dumps(idx.search(a.query,limit=a.limit,phrase=a.phrase),indent=2))
        elif a.command=='stats':print(json.dumps(idx.stats()))
        else:print(json.dumps({'deleted':idx.delete(a.id)}))
    finally:idx.close()
if __name__=='__main__':main()
