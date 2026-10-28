"""End-to-end process evaluation using a frozen training baseline."""
from collections import Counter,defaultdict
from .models import QualitySpec,Reading
from .stats import baseline,capability,defect_rate
from .rules import shewhart
from .ewma import ewma
from .cusum import cusum
from .changepoint import best_split
from .risk import lot_risk

def evaluate(training: list[Reading], production: list[Reading], spec: QualitySpec) -> dict:
    if len(training)<8 or not production: raise ValueError("need >=8 training and nonempty production")
    group=training+production
    if any(x.metric!=spec.metric for x in group): raise ValueError("metric mismatch")
    if len({(x.line,x.machine) for x in group})!=1: raise ValueError("mixed production assets")
    ref=baseline([r.value for r in training])
    values=[r.value for r in production]
    s=shewhart(values,ref)
    ewma_trace,e=ewma(values,ref)
    cusum_trace,c=cusum(values,ref)
    findings=[{"event_id":production[signal.index].event_id,"lot":production[signal.index].lot,**signal.as_dict()} for signal in s+e+c]
    findings.sort(key=lambda x:(x["index"],x["rule"]))
    by_lot=defaultdict(list)
    for r in production: by_lot[r.lot].append(r)
    severity=defaultdict(Counter)
    for f in findings: severity[f["lot"]][f["severity"]]+=1
    lots={}
    for lot,items in sorted(by_lot.items()):
        frac=defect_rate([r.value for r in items],spec)
        lots[lot]={"readings":len(items),"defect_fraction":frac,**lot_risk(frac,severity[lot]["critical"],severity[lot]["warning"],len(items))}
    return {"asset":{"line":production[0].line,"machine":production[0].machine,"metric":spec.metric},
            "spec":{"lsl":spec.lsl,"usl":spec.usl,"target":spec.target,"unit":spec.unit},
            "baseline":ref.__dict__,"production_count":len(production),"defect_fraction":defect_rate(values,spec),
            "capability":capability(values,spec),"change_point":best_split(values),
            "signal_counts":dict(Counter(f["rule"] for f in findings)),"signals":findings,"lots":lots,
            "chart":{"values":values,"ewma":ewma_trace,"cusum_positive":[p for p,_ in cusum_trace],"cusum_negative":[m for _,m in cusum_trace]},
            "limitations":["No automatic release decisions","SPC limits require stable representative baseline","Multiple rules increase false-alarm probability","Capability indices assume normality and process stability"]}
