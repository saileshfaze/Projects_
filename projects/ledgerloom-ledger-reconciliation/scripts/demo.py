"""End-to-end reproducible demo with a temporary database."""
import json
import tempfile
from pathlib import Path
from ledgerloom.journal import Journal
from ledgerloom.model import Entry,Posting
from ledgerloom.reconcile import reconcile
from ledgerloom.report import balance_svg

def run(output=None):
    with tempfile.TemporaryDirectory() as tmp:
        j=Journal(Path(tmp)/"ledger.sqlite3")
        for i in range(12):
            amount=1000+i*150
            j.post(Entry(f"demo-{i}",f"2026-10-{i+1:02d}","synthetic receipt",
                         (Posting("cash",amount),Posting("revenue",-amount)),f"SYN-{i:04d}"))
        statements=[{"day":f"2026-10-{i+1:02d}","amount":1000+i*150,"reference":f"SYN-{i:04d}"} for i in range(12)]
        result=reconcile(j.lines("cash"),statements)
        assert j.verify() and len(result["matched"])==12
        report={"audit_valid":j.verify(),"head":j.head(),"trial_balance":j.trial_balance(),
                "matched":len(result["matched"]),"unmatched":len(result["unmatched_statements"])}
        if output:
            out=Path(output);out.mkdir(parents=True,exist_ok=True)
            (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
            (out/"trial-balance.svg").write_text(balance_svg(j.trial_balance()),encoding="utf-8")
        return report
if __name__=="__main__":
    print(json.dumps(run("sample-output"),indent=2))
