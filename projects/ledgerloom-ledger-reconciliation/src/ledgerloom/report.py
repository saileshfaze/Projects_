"""Pure SVG chart generator for account balances."""
from html import escape

def balance_svg(balances):
    items=list(sorted(balances.items()))
    width=760;height=90+max(1,len(items))*46
    scale=max((abs(v) for _,v in items),default=1) or 1
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#101827"/>',
           '<text x="25" y="35" fill="white" font-size="20">LedgerLoom trial balance (minor units)</text>']
    for i,(name,value) in enumerate(items):
        y=75+i*46
        parts.append(f'<text x="25" y="{y}" fill="#d5e3f0" font-size="14">{escape(name)}</text>')
        parts.append(f'<rect x="255" y="{y-15}" width="{int(abs(value)/scale*350)}" height="20" fill="{("#56c4a8" if value>=0 else "#f5a76b")}"/>')
        parts.append(f'<text x="620" y="{y}" fill="white" font-size="14">{value}</text>')
    return "".join(parts)+"</svg>"
