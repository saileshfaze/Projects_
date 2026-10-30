"""SQLite scenario snapshots and tamper-evident append-only event chain."""
import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path

def canonical(value)->str:
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def digest(value)->str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()

class Store:
    def __init__(self,path:str='skyweave.db'):
        self.path=path
        with self.connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, scenario TEXT NOT NULL, report TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, payload_hash TEXT NOT NULL, previous_hash TEXT NOT NULL, entry_hash TEXT NOT NULL);""")

    def connect(self):
        db=sqlite3.connect(self.path,timeout=10)
        db.row_factory=sqlite3.Row
        return db

    def save(self,scenario:dict,report:dict)->str:
        key=digest({'scenario':scenario,'report':report})
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT id FROM runs WHERE id=?',(key,)).fetchone():return key
            db.execute('INSERT INTO runs VALUES (?,?,?,?)',(key,canonical(scenario),canonical(report),datetime.now(timezone.utc).isoformat()))
            row=db.execute('SELECT entry_hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
            previous=row['entry_hash'] if row else '0'*64
            payload_hash=digest({'run_id':key})
            entry_hash=digest({'action':'run.saved','payload_hash':payload_hash,'previous_hash':previous})
            db.execute('INSERT INTO audit (action,payload_hash,previous_hash,entry_hash) VALUES (?,?,?,?)',('run.saved',payload_hash,previous,entry_hash))
        return key

    def load(self,key:str)->dict|None:
        with self.connect() as db:
            row=db.execute('SELECT report FROM runs WHERE id=?',(key,)).fetchone()
        return json.loads(row['report']) if row else None

    def verify(self)->bool:
        previous='0'*64
        with self.connect() as db:
            rows=db.execute('SELECT * FROM audit ORDER BY seq').fetchall()
            runs=db.execute('SELECT id,scenario,report FROM runs').fetchall()
        for row in rows:
            if row['previous_hash']!=previous:return False
            if row['entry_hash']!=digest({'action':row['action'],'payload_hash':row['payload_hash'],'previous_hash':previous}):return False
            previous=row['entry_hash']
        for run in runs:
            if digest({'scenario':json.loads(run['scenario']),'report':json.loads(run['report'])})!=run['id']:return False
        return True
