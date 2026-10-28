"""Application service isolating storage and analytics from transport."""
from .store import Store
from .models import Reading,QualitySpec
from .engine import evaluate
class QualityService:
    def __init__(self,db_path:str): self.db_path=db_path
    def set_spec(self,spec:QualitySpec):
        db=Store(self.db_path)
        try: db.put_spec(spec)
        finally: db.close()
    def ingest(self,readings:list[Reading])->dict:
        db=Store(self.db_path);inserted=0
        try:
            for r in readings: inserted+=int(db.ingest(r))
            return {'inserted':inserted,'replayed':len(readings)-inserted}
        finally: db.close()
    def report(self,line:str,machine:str,metric:str,baseline_lot:str='baseline')->dict:
        db=Store(self.db_path)
        try:
            spec=db.get_spec(metric)
            if spec is None: raise ValueError('specification not found')
            items=db.readings(line,machine,metric)
            training=[r for r in items if r.lot==baseline_lot]
            production=[r for r in items if r.lot!=baseline_lot]
            return evaluate(training,production,spec)
        finally: db.close()
    def audit(self)->dict:
        db=Store(self.db_path)
        try: return db.verify()
        finally: db.close()
