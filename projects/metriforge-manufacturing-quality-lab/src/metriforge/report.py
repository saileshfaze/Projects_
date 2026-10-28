"""Deterministic JSON and SVG control-chart report rendering (no external CDN)."""
import json,html
from pathlib import Path

def save_json(report:dict,path:str):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')

def svg_chart(report:dict,width:int=960,height:int=420)->str:
    values=report['chart']['values']; base=report['baseline']; spec=report['spec']
    if not values: raise ValueError('empty chart')
    low=min(values+[spec['lsl'],base['center']-3*base['sigma']]); high=max(values+[spec['usl'],base['center']+3*base['sigma']]); margin=max((high-low)*.08,.1);low-=margin;high+=margin
    x0,y0,x1,y1=80,40,width-30,height-65
    def pt(i,v):return f'{x0+(x1-x0)*i/max(1,len(values)-1):.1f},{y1-(v-low)/(high-low)*(y1-y0):.1f}'
    lines=[]
    for value,label,color in [(spec['lsl'],'LSL','#b45309'),(spec['usl'],'USL','#b45309'),(base['center'],'Center','#0f766e'),(base['center']-3*base['sigma'],'-3σ','#be123c'),(base['center']+3*base['sigma'],'+3σ','#be123c')]:
        y=pt(0,value).split(',')[1]
        lines.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{color}" stroke-dasharray="5 5" opacity=".7"/><text x="{x1-4}" y="{float(y)-4:.1f}" fill="{color}" text-anchor="end" font-size="11">{label}</text>')
    points=' '.join(pt(i,v) for i,v in enumerate(values))
    title=html.escape(f"MetriForge · {report['asset']['machine']} · {report['asset']['metric']}")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Manufacturing control chart"><rect width="100%" height="100%" fill="#f8fafc"/><text x="{x0}" y="25" font-family="sans-serif" font-size="18" fill="#0f172a">{title}</text><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="#cbd5e1"/>{"".join(lines)}<polyline points="{points}" fill="none" stroke="#1d4ed8" stroke-width="1.8"/><text x="{x0}" y="{height-20}" fill="#475569" font-size="12">Synthetic demonstration · sequence index</text></svg>\n'

def save_svg(report:dict,path:str):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg_chart(report),encoding='utf-8')
