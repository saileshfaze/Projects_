"""Regenerate tracked synthetic CSVs from a fixed seed."""
import csv
from pathlib import Path
from metriforge.csvio import save_readings
from metriforge.synthetic import generate

def run(out='data/synthetic'):
    baseline,production,labels=generate()
    path=Path(out);path.mkdir(parents=True,exist_ok=True)
    save_readings(str(path/'baseline.csv'),baseline)
    save_readings(str(path/'production.csv'),production)
    with (path/'labels.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['event_id','shift','drift','spike']);writer.writeheader();writer.writerows(labels)
if __name__=='__main__':run()
