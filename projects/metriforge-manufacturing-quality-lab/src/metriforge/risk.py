"""Transparent lot-level quality triage score, not a calibrated failure probability."""
def lot_risk(defect_fraction: float, critical: int, warning: int, n: int) -> dict:
    if n<=0 or not 0<=defect_fraction<=1 or min(critical,warning)<0: raise ValueError("invalid lot metrics")
    score=min(100.,100*(0.6*defect_fraction+0.25*min(critical/n,1)+0.15*min(warning/n,1)))
    tier="hold" if score>=12 or critical>=3 else "review" if score>=3 or critical>0 else "monitor"
    return {"score":round(score,2),"tier":tier,"note":"heuristic triage; requires human quality approval"}
