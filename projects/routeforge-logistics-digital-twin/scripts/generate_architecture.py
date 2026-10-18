"""Generate a portable SVG architecture diagram without external assets."""
from pathlib import Path

svg = """<svg xmlns="http://www.w3.org/2000/svg" width="980" height="180" viewBox="0 0 980 180">
<rect width="980" height="180" fill="#f8fafc"/>
<g font-family="sans-serif" font-size="16" text-anchor="middle">
<rect x="20" y="50" width="180" height="75" rx="12" fill="#dbeafe" stroke="#2563eb"/>
<text x="110" y="83">Synthetic inputs</text><text x="110" y="105">+ validation</text>
<rect x="260" y="50" width="180" height="75" rx="12" fill="#dcfce7" stroke="#16a34a"/>
<text x="350" y="83">Feasible insertion</text><text x="350" y="105">+ relocation</text>
<rect x="500" y="50" width="180" height="75" rx="12" fill="#fef3c7" stroke="#d97706"/>
<text x="590" y="83">Scenario engine</text><text x="590" y="105">+ analytics</text>
<rect x="740" y="50" width="220" height="75" rx="12" fill="#ede9fe" stroke="#7c3aed"/>
<text x="850" y="83">REST / SQLite</text><text x="850" y="105">+ SVG / HTML</text>
</g><g stroke="#334155" stroke-width="3" fill="none"><path d="M200 87H260"/><path d="M440 87H500"/><path d="M680 87H740"/></g>
</svg>"""
path = Path("assets/architecture.svg")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(svg, encoding="utf-8")
print(path)
