"""Transactional SQLite journal with immutable postings and hash-linked events."""
import hashlib
import json
import sqlite3
from pathlib import Path
from .model import Entry, LedgerError

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def digest(prev, payload):
    return hashlib.sha256((prev + "\n" + canonical(payload)).encode()).hexdigest()

class Journal:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, key TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS lines (event_seq INTEGER NOT NULL, line_no INTEGER NOT NULL,
                    day TEXT NOT NULL, account TEXT NOT NULL, amount INTEGER NOT NULL,
                    reference TEXT NOT NULL, PRIMARY KEY(event_seq,line_no));
                CREATE INDEX IF NOT EXISTS idx_lines_account_day ON lines(account,day);
            """)
    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)
    def post(self, entry: Entry):
        payload = {"key": entry.key, "day": entry.day, "description": entry.description,
                   "reference": entry.reference,
                   "postings": [{"account": p.account, "amount": p.amount} for p in entry.postings]}
        encoded = canonical(payload)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT seq,payload FROM events WHERE key=?", (entry.key,)).fetchone()
            if prior:
                if prior[1] != encoded:
                    raise LedgerError("idempotency key reused with different payload")
                return prior[0]
            row = db.execute("SELECT seq,hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            seq, prev = (row[0]+1,row[1]) if row else (1,"0"*64)
            hashed = digest(prev, payload)
            db.execute("INSERT INTO events VALUES (?,?,?,?,?)", (seq,entry.key,encoded,prev,hashed))
            for idx,p in enumerate(entry.postings):
                db.execute("INSERT INTO lines VALUES (?,?,?,?,?,?)",
                           (seq,idx,entry.day,p.account,p.amount,entry.reference))
        return seq
    def verify(self):
        with self._connect() as db:
            events = db.execute("SELECT seq,payload,prev_hash,hash FROM events ORDER BY seq").fetchall()
            prev = "0"*64
            for expected,(seq,encoded,linked,hashed) in enumerate(events,1):
                if seq != expected or linked != prev:
                    return False
                try:
                    payload = json.loads(encoded)
                except json.JSONDecodeError:
                    return False
                if canonical(payload) != encoded or digest(prev,payload) != hashed:
                    return False
                lines = db.execute("SELECT account,amount,reference,day FROM lines WHERE event_seq=? ORDER BY line_no", (seq,)).fetchall()
                expected_lines = [(p["account"],p["amount"],payload["reference"],payload["day"]) for p in payload["postings"]]
                if lines != expected_lines or sum(row[1] for row in lines) != 0:
                    return False
                prev = hashed
            if db.execute("SELECT COUNT(*) FROM lines WHERE event_seq NOT IN (SELECT seq FROM events)").fetchone()[0]:
                return False
            return True
    def lines(self, account=None, through=None):
        query = "SELECT event_seq,day,account,amount,reference FROM lines WHERE 1=1"
        params=[]
        if account is not None:
            query += " AND account=?";params.append(account)
        if through is not None:
            query += " AND day<=?";params.append(through)
        query += " ORDER BY day,event_seq"
        with self._connect() as db:
            return [dict(zip(("seq","day","account","amount","reference"),row)) for row in db.execute(query,params)]
    def trial_balance(self, through=None):
        result={}
        for line in self.lines(through=through):
            result[line["account"]]=result.get(line["account"],0)+line["amount"]
        return dict(sorted(result.items()))
    def head(self):
        with self._connect() as db:
            row=db.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            return row[0] if row else "0"*64
