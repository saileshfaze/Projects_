"""Render a small reproducible station/event schematic."""
from pathlib import Path
from seismoscope.synthetic import network

def main():
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 440">','<rect width="440" height="440" fill="#101827"/>']
    for s in network().values():
        x=220+s.x_km*8;y=220-s.y_km*8
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#38bdf8"/><text x="{x+10}" y="{y-8}" fill="white" font-size="13">{s.code}</text>')
    parts.append('<circle cx="236" cy="252" r="9" fill="#fb923c"/><text x="248" y="267" fill="white" font-size="13">Synthetic source</text></svg>')
    out=Path('assets/station-map.svg');out.parent.mkdir(exist_ok=True);out.write_text(''.join(parts))
if __name__=='__main__':main()
