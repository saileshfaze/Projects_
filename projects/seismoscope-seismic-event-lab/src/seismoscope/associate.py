"""Simple coincidence association using a bounded arrival window."""
from .models import Pick

def associate(picks, min_stations=3, window_s=8.0):
    if min_stations<2 or window_s<=0:raise ValueError("invalid association parameters")
    picks=sorted(picks,key=lambda p:p.time_s)
    clusters=[]
    i=0
    while i<len(picks):
        start=picks[i].time_s
        group={}
        j=i
        while j<len(picks) and picks[j].time_s-start<=window_s:
            group.setdefault(picks[j].station,picks[j]);j+=1
        if len(group)>=min_stations:
            clusters.append(list(group.values()));i=j
        else:i+=1
    return clusters
