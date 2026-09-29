from sqlalchemy import create_engine,text
from sqlalchemy.engine import Engine
DDL="""CREATE TABLE IF NOT EXISTS decisions (transaction_id TEXT PRIMARY KEY,account_id TEXT NOT NULL,amount_eur REAL NOT NULL,score REAL NOT NULL,decision TEXT NOT NULL,reasons TEXT NOT NULL,event_time TEXT NOT NULL)"""
def build_engine(url:str)->Engine:
    engine=create_engine(url,connect_args={"check_same_thread":False} if url.startswith("sqlite") else {})
    with engine.begin() as conn: conn.execute(text(DDL))
    return engine
def save_decision(engine:Engine,tx,decision)->None:
    with engine.begin() as conn:
        conn.execute(text("""INSERT OR REPLACE INTO decisions (transaction_id,account_id,amount_eur,score,decision,reasons,event_time) VALUES (:tid,:aid,:amount,:score,:decision,:reasons,:event_time)"""),{"tid":tx.transaction_id,"aid":tx.account_id,"amount":tx.amount_eur,"score":decision.score,"decision":decision.decision,"reasons":",".join(decision.reasons),"event_time":tx.event_time.isoformat()})
def summary(engine:Engine)->dict:
    with engine.begin() as conn:
        row=conn.execute(text("""SELECT COUNT(*) n,COALESCE(AVG(score),0) avg_score,SUM(CASE WHEN decision='block' THEN 1 ELSE 0 END) blocked,SUM(CASE WHEN decision='review' THEN 1 ELSE 0 END) review FROM decisions""")).mappings().one()
    return dict(row)
