"""Append-only JSONL hash chain for local demonstration; not tamper-proof storage."""
import hashlib, json
from pathlib import Path

def append(path: str, event: dict) -> dict:
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    previous='0'*64
    if p.exists():
        records=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        if records: previous=records[-1]['hash']
    payload={'previous':previous,'event':event}
    payload['hash']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with p.open('a') as f: f.write(json.dumps(payload,sort_keys=True)+'\n')
    return payload

def verify(path: str) -> bool:
    previous='0'*64
    for line in Path(path).read_text().splitlines():
        record=json.loads(line)
        digest=hashlib.sha256(json.dumps({'previous':record['previous'],'event':record['event']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if record['previous']!=previous or record['hash']!=digest:return False
        previous=digest
    return True
