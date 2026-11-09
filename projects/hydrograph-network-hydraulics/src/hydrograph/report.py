"""Offline JSON and self-contained SVG network reports."""
import html,json
from pathlib import Path

def write_json(path,object):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(object,indent=2,sort_keys=True)+'\n',encoding='utf8')

def svg(network,solution):
    names=[network.reservoir,*network.demands]
    points={name:(90+(i%3)*240,100+(i//3)*190) for i,name in enumerate(names)}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="540" viewBox="0 0 760 540">',
           '<rect width="760" height="540" fill="#f7fafc"/>',
           '<text x="24" y="35" font-size="22">HydroGraph synthetic network</text>']
    for p in network.pipes:
        x1,y1=points[p.start];x2,y2=points[p.end]
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#447799" stroke-width="4"/>')
        parts.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-8}" font-size="12">{html.escape(p.name)}: {solution.flows[p.name]:.2f}</text>')
    for name,(x,y) in points.items():
        parts.append(f'<circle cx="{x}" cy="{y}" r="26" fill="#d6eaf3" stroke="#19486a"/>')
        parts.append(f'<text x="{x-30}" y="{y+42}" font-size="14">{html.escape(name)} {solution.heads[name]:.2f}m</text>')
    parts.append('</svg>')
    return '\n'.join(parts)+'\n'
