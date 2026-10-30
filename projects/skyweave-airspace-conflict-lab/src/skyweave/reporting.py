"""Portable JSON, GeoJSON, CSV, and SVG artifacts without external services."""
from dataclasses import asdict
from html import escape
from .models import Flight,Conflict

def geojson(flights:tuple[Flight,...])->dict:
    return {'type':'FeatureCollection','features':[{'type':'Feature','properties':{'callsign':f.callsign,'start_s':f.fixes[0].t,'end_s':f.fixes[-1].t},'geometry':{'type':'LineString','coordinates':[[p.lon,p.lat,p.alt_ft] for p in f.fixes]}} for f in flights]}

def conflict_csv(conflicts:list[Conflict])->str:
    cols=list(Conflict.__dataclass_fields__)
    lines=[','.join(cols)]
    for c in conflicts: lines.append(','.join(str(getattr(c,k)) for k in cols))
    return '\n'.join(lines)+'\n'

def timeline_svg(conflicts:list[Conflict],width:int=900)->str:
    height=110+max(1,len(conflicts))*36
    xmax=max([c.exit_s for c in conflicts]+[1.])
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#101b2d"/>',
        '<text x="25" y="36" fill="#e2e8f0" font-family="sans-serif" font-size="20">SkyWeave · conflict windows</text>',
        '<line x1="210" y1="60" x2="870" y2="60" stroke="#94a3b8"/>']
    for i,c in enumerate(conflicts):
        y=86+i*36
        x=210+660*c.entry_s/xmax; w=max(2,660*(c.exit_s-c.entry_s)/xmax)
        elements += [f'<text x="25" y="{y+13}" fill="#cbd5e1" font-family="monospace" font-size="13">{escape(c.a)} / {escape(c.b)}</text>',f'<rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="18" rx="4" fill="#fb7185"/>']
    elements.append('</svg>')
    return '\n'.join(elements)
