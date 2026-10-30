"""Continuous-time separation detection for piecewise-linear synthetic trajectories.

For each overlapping segment pair, solve the quadratic horizontal-separation
inequality and the linear vertical-separation inequality. Their intersection
is a conflict interval; adjacent intervals are merged per aircraft pair.
"""
from __future__ import annotations
from math import sqrt
from itertools import combinations
from .models import Flight,Conflict,Thresholds
from .geometry import project,NM_M,FT_M,dot
from .interpolate import at

EPS=1e-9

def _horizontal_window(p:tuple[float,float],v:tuple[float,float],limit:float,duration:float)->tuple[float,float]|None:
    aa=dot(v,v); bb=2*dot(p,v); cc=dot(p,p)-limit*limit
    if aa<EPS:
        return (0.0,duration) if cc<0 else None
    disc=bb*bb-4*aa*cc
    if disc<=0:
        return None
    lo=(-bb-sqrt(disc))/(2*aa); hi=(-bb+sqrt(disc))/(2*aa)
    lo=max(0.,lo); hi=min(duration,hi)
    return (lo,hi) if hi-lo>EPS else None

def _vertical_window(z:float,vz:float,limit:float,duration:float)->tuple[float,float]|None:
    if abs(vz)<EPS:
        return (0.,duration) if abs(z)<limit else None
    a=(-limit-z)/vz; b=(limit-z)/vz
    lo=max(0.,min(a,b)); hi=min(duration,max(a,b))
    return (lo,hi) if hi-lo>EPS else None

def _pair_intervals(a:Flight,b:Flight,thresholds:Thresholds,ref:tuple[float,float]):
    windows=[]
    for fa,fb in zip(a.fixes,a.fixes[1:]):
        for ga,gb in zip(b.fixes,b.fixes[1:]):
            start=max(fa.t,ga.t); end=min(fb.t,gb.t)
            if end-start<=EPS: continue
            pa=at(a,start); pb=at(b,start)
            qa=at(a,end); qb=at(b,end)
            assert pa and pb and qa and qb
            p1=project(pa.lat,pa.lon,*ref); p2=project(pb.lat,pb.lon,*ref)
            q1=project(qa.lat,qa.lon,*ref); q2=project(qb.lat,qb.lon,*ref)
            delta=(p1[0]-p2[0],p1[1]-p2[1])
            d_end=(q1[0]-q2[0],q1[1]-q2[1]); dt=end-start
            v=((d_end[0]-delta[0])/dt,(d_end[1]-delta[1])/dt)
            z=(pa.alt_ft-pb.alt_ft)*FT_M
            vz=((qa.alt_ft-qb.alt_ft)*FT_M-z)/dt
            h=_horizontal_window(delta,v,thresholds.horizontal_nm*NM_M,dt)
            w=_vertical_window(z,vz,thresholds.vertical_ft*FT_M,dt)
            if h is None or w is None: continue
            lo=max(h[0],w[0]); hi=min(h[1],w[1])
            if hi-lo<=EPS: continue
            # Closest horizontal point inside the actual conflict interval.
            best=max(lo,min(hi,-dot(delta,v)/dot(v,v))) if dot(v,v)>EPS else lo
            d=sqrt((delta[0]+best*v[0])**2+(delta[1]+best*v[1])**2)/NM_M
            windows.append((start+lo,start+hi,start+best,d,abs(z+best*vz)/FT_M))
    return windows

def detect(flights:tuple[Flight,...],thresholds:Thresholds=Thresholds())->list[Conflict]:
    if not flights:return []
    ref=(sum(f.fixes[0].lat for f in flights)/len(flights),sum(f.fixes[0].lon for f in flights)/len(flights))
    out=[]
    for a,b in combinations(sorted(flights,key=lambda f:f.callsign),2):
        windows=sorted(_pair_intervals(a,b,thresholds,ref))
        if not windows: continue
        merged=[]
        for w in windows:
            if merged and w[0]<=merged[-1][1]+1e-7:
                old=merged[-1]
                best=w if w[3]<old[3] else old
                merged[-1]=(old[0],max(old[1],w[1]),best[2],best[3],best[4])
            else: merged.append(w)
        for lo,hi,tcpa,h,z in merged:
            out.append(Conflict(a.callsign,b.callsign,round(lo,4),round(hi,4),round(tcpa,4),round(h,5),round(z,2)))
    return sorted(out,key=lambda c:(c.entry_s,c.a,c.b))
