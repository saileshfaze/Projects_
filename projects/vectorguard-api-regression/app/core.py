import json
from difflib import SequenceMatcher

def fingerprint(payload):
    if isinstance(payload,dict):
        return {key:fingerprint(value) for key,value in sorted(payload.items())}
    if isinstance(payload,list):
        return [fingerprint(payload[0])] if payload else []
    return type(payload).__name__

def compare(before,after):
    a,b=fingerprint(before),fingerprint(after)
    return {'breaking':_missing(a,b),'structure_changed':a!=b,'text_similarity':SequenceMatcher(None,json.dumps(before,sort_keys=True),json.dumps(after,sort_keys=True)).ratio()}

def _missing(a,b):
    if isinstance(a,dict):
        return not isinstance(b,dict) or any(k not in b or _missing(v,b[k]) for k,v in a.items())
    return type(a) is not type(b) or (isinstance(a,str) and a!=b)
