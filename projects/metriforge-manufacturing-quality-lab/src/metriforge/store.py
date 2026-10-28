"""SQLite-backed idempotent event log with immutable payload checks and SHA-256 chain."""
import hashlib,json,sqlite3
from pathlib import Path
from .models import Reading,QualitySpec

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)
class Store:
    def __init__(self,path: str):
        self.path=path
        Path(path).parent.mkdir(parents=True,exist_ok=True) if path!=':memory:' else None
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS specs(metric TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS readings(seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL, prev_hash TEXT NOT NULL, digest TEXT NOT NULL);
        """)
        self.db.commit()
    def close(self): self.db.close()
    def put_spec(self,spec:QualitySpec):
        payload=canonical(spec.__dict__)
        with self.db: self.db.execute('INSERT INTO specs(metric,payload) VALUES(?,?) ON CONFLICT(metric) DO UPDATE SET payload=excluded.payload',(spec.metric,payload))
    def get_spec(self,metric:str)->QualitySpec|None:
        row=self.db.execute('SELECT payload FROM specs WHERE metric=?',(metric,)).fetchone()
        return QualitySpec(**json.loads(row['payload'])) if row else None
    def ingest(self,reading:Reading)->bool:
        payload=canonical(reading.__dict__)
        with self.db:
            existing=self.db.execute('SELECT payload FROM readings WHERE event_id=?',(reading.event_id,)).fetchone()
            if existing:
                if existing['payload']!=payload: raise ValueError('event_id conflict: immutable payload differs')
                return False
            previous=self.db.execute('SELECT digest FROM readings ORDER BY seq DESC LIMIT 1').fetchone()
            prev=previous['digest'] if previous else '0'*64
            digest=hashlib.sha256((prev+'|'+payload).encode()).hexdigest()
            self.db.execute('INSERT INTO readings(event_id,payload,prev_hash,digest) VALUES(?,?,?,?)',(reading.event_id,payload,prev,digest))
            return True
    def readings(self,line:str,machine:str,metric:str,lot:str|None=None)->list[Reading]:
        rows=self.db.execute('SELECT payload FROM readings ORDER BY seq').fetchall()
        items=[Reading(**json.loads(row['payload'])) for row in rows]
        items=[r for r in items if (r.line,r.machine,r.metric)==(line,machine,metric) and (lot is None or r.lot==lot)]
        return sorted(items,key=lambda r:(r.timestamp,r.event_id))
    def verify(self)->dict:
        rows=self.db.execute('SELECT seq,payload,prev_hash,digest FROM readings ORDER BY seq').fetchall()
        prev='0'*64
        for row in rows:
            expected=hashlib.sha256((prev+'|'+row['payload']).encode()).hexdigest()
            if row['prev_hash']!=prev or row['digest']!=expected:
                return {"valid":False,"events":len(rows),"first_bad_seq":row['seq']}
            prev=expected
        return {"valid":True,"events":len(rows),"head":prev}
