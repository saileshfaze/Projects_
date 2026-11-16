"""Deterministic multi-server FIFO event simulator, with bounded waiting."""
from collections import deque
from heapq import heappush, heappop
from math import isfinite

def validate(s):
    if type(s.get('servers')) is not int or s['servers'] < 1: raise ValueError('servers must be positive integer')
    cap = s.get('waiting_capacity')
    if cap is not None and (type(cap) is not int or cap < 0): raise ValueError('invalid waiting capacity')
    jobs = s.get('jobs')
    if not isinstance(jobs,list): raise ValueError('jobs must be a list')
    seen=set()
    for j in jobs:
        if not isinstance(j,dict) or not isinstance(j.get('id'),str) or not j['id'] or j['id'] in seen: raise ValueError('invalid or duplicate id')
        seen.add(j['id'])
        for k in ('arrival','duration'):
            v=j.get(k)
            if type(v) not in (int,float) or not isfinite(v) or v<0: raise ValueError('invalid '+k)
    return True

def percentile(values,p):
    if not values:return 0.0
    a=sorted(values); pos=(len(a)-1)*p; lo=int(pos); hi=min(lo+1,len(a)-1)
    return a[lo]+(a[hi]-a[lo])*(pos-lo)

def simulate(s):
    validate(s)
    n=s['servers']; capacity=s.get('waiting_capacity')
    jobs=sorted(s['jobs'],key=lambda j:(j['arrival'],j['id']))
    free=list(range(n)); busy=[]; waiting=deque(); results=[]; rejected=[]; events=[]
    busy_time=[0.0]*n
    def start(job,server,t):
        end=t+job['duration']; busy_time[server]+=job['duration']
        rec={'id':job['id'],'server':server,'arrival':job['arrival'],'start':t,'finish':end,'wait':t-job['arrival'],'sojourn':end-job['arrival']}
        results.append(rec); events.append({'time':t,'kind':'start','id':job['id'],'server':server})
        heappush(busy,(end,server,job['id']))
    def release_until(t):
        while busy and busy[0][0]<=t:
            finish,server,jid=heappop(busy); events.append({'time':finish,'kind':'finish','id':jid,'server':server})
            if waiting:start(waiting.popleft(),server,finish)
            else:heappush(free,server)
    for job in jobs:
        t=job['arrival'];release_until(t)
        events.append({'time':t,'kind':'arrival','id':job['id']})
        if free:
            from heapq import heappop as pop
            start(job,pop(free),t)
        elif capacity is None or len(waiting)<capacity:waiting.append(job)
        else:
            rejected.append(job['id']);events.append({'time':t,'kind':'reject','id':job['id']})
    release_until(float('inf'))
    makespan=max((r['finish'] for r in results),default=0)
    waits=[r['wait'] for r in results]
    results.sort(key=lambda r:r['id'])
    return {'accepted':len(results),'rejected':rejected,'total':len(jobs),'makespan':makespan,'mean_wait':sum(waits)/len(waits) if waits else 0.0,'p95_wait':percentile(waits,.95),'utilization':[t/makespan if makespan else 0.0 for t in busy_time],'jobs':results,'events':events}
