"""Strict CSV import/export with deterministic column ordering."""
import csv
from pathlib import Path
from .models import Reading
FIELDS=list(Reading.__dataclass_fields__)
def load_readings(path:str)->list[Reading]:
    with open(path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if not set(FIELDS).issubset(reader.fieldnames or []): raise ValueError('missing CSV fields')
        return [Reading(**{**{k:row[k] for k in FIELDS if k!='value'},'value':float(row['value'])}) for row in reader]
def save_readings(path:str,items:list[Reading]):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader()
        for r in items: writer.writerow(r.__dict__)
