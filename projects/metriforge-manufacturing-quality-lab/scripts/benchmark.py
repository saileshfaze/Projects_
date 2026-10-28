"""Synthetic demonstration: alarm onset relative to an injected step change."""
import json
from metriforge.synthetic import generate
from metriforge.stats import baseline
from metriforge.rules import shewhart
from metriforge.ewma import ewma
from metriforge.cusum import cusum

def run():
    train,prod,labels=generate();ref=baseline([x.value for x in train]);v=[x.value for x in prod]
    methods={'shewhart':[s.index for s in shewhart(v,ref)],'ewma':[s.index for s in ewma(v,ref)[1]],'cusum':[s.index for s in cusum(v,ref)[1]]}
    start=next(i for i,row in enumerate(labels) if row['shift'])
    return {'seed':2026,'step_index':start,'first_alarm':{k:min(points) if points else None for k,points in methods.items()},'signal_counts':{k:len(points) for k,points in methods.items()},'note':'synthetic single scenario, not a validated sensitivity or specificity benchmark'}
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
