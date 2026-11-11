"""Trace serialization with strict hex and bounded input size."""
import json
from .wire import Frame, encode, decode
from .errors import FrameError
def export_trace(frames):
    return json.dumps([{"kind":f.kind,"sequence":f.sequence,"wire_hex":encode(f).hex()} for f in frames],indent=2)
def import_trace(raw):
    obj=json.loads(raw)
    if not isinstance(obj,list) or len(obj)>10000: raise FrameError("trace must be a bounded list")
    result=[]
    for item in obj:
        if not isinstance(item,dict) or not isinstance(item.get("wire_hex"),str): raise FrameError("invalid trace record")
        frame=decode(bytes.fromhex(item["wire_hex"]))
        if frame.kind!=item.get("kind") or frame.sequence!=item.get("sequence"): raise FrameError("trace metadata mismatch")
        result.append(frame)
    return result
