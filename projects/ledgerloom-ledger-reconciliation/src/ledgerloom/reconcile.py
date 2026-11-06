"""Conservative, deterministic one-to-one statement reconciliation."""
from datetime import date
from .model import LedgerError

def reconcile(ledger_lines, statements, tolerance_days=2):
    if type(tolerance_days) is not int or tolerance_days < 0:
        raise LedgerError("tolerance_days must be a nonnegative integer")
    available={i:line for i,line in enumerate(ledger_lines)}
    matched=[]; ambiguous=[]; unmatched=[]
    for row in statements:
        if type(row.get("amount")) is not int:
            raise LedgerError("statement amounts must be integer minor units")
        try:
            day=date.fromisoformat(row["day"])
        except (KeyError,ValueError,TypeError) as exc:
            raise LedgerError("invalid statement date") from exc
        candidates=[]
        for i,line in available.items():
            if line["amount"] != row["amount"]:
                continue
            delta=abs((day-date.fromisoformat(line["day"])).days)
            if delta > tolerance_days:
                continue
            exact = bool(row.get("reference")) and row["reference"] == line["reference"]
            candidates.append((0 if exact else 1,delta,i))
        if not candidates:
            unmatched.append(row);continue
        candidates.sort()
        best_rank=candidates[0][:2]
        best=[item for item in candidates if item[:2]==best_rank]
        if len(best)>1:
            ambiguous.append({"statement":row,"candidate_count":len(best)});continue
        idx=best[0][2]
        matched.append({"statement":row,"ledger":available.pop(idx)})
    return {"matched":matched,"ambiguous":ambiguous,"unmatched_statements":unmatched,
            "unmatched_ledger":list(available.values())}
