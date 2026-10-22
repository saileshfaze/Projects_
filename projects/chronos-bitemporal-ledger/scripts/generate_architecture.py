"""Generate a portable SVG architecture diagram without third-party packages."""

from pathlib import Path
from xml.sax.saxutils import escape

BOXES = [
    (25, 110, "REST API / CLI", "FastAPI · Pydantic"),
    (260, 110, "Correction engine", "idempotency · intervals"),
    (495, 110, "SQLite ledger", "versions · operations"),
    (730, 110, "Audit verifier", "SHA-256 · closures"),
]


def render() -> str:
    blocks = []
    for x, y, title, subtitle in BOXES:
        blocks.append(f'<rect x="{x}" y="{y}" width="205" height="105" rx="13" fill="#12233d" stroke="#48b0e5" stroke-width="2"/>')
        blocks.append(f'<text x="{x+102}" y="{y+42}" fill="white" font-size="18" text-anchor="middle" font-weight="bold">{escape(title)}</text>')
        blocks.append(f'<text x="{x+102}" y="{y+72}" fill="#b8d8ef" font-size="13" text-anchor="middle">{escape(subtitle)}</text>')
    for x in [232, 467, 702]:
        blocks.append(f'<path d="M{x} 162 h23" stroke="#20c997" stroke-width="3" marker-end="url(#arrow)"/>')
    return ('''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="310" viewBox="0 0 960 310">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#20c997"/></marker></defs>
<rect width="960" height="310" fill="#0b1424"/>
<text x="480" y="52" fill="white" font-size="26" text-anchor="middle" font-family="Arial">Chronos Bitemporal Ledger</text>
<text x="480" y="80" fill="#9fb3ca" font-size="14" text-anchor="middle" font-family="Arial">Valid-time corrections · System-time history · Tenant audit chain</text>
''' + "\n".join(blocks) + '''
<text x="480" y="275" fill="#9fb3ca" font-size="13" text-anchor="middle" font-family="Arial">ACID write transaction · Half-open intervals · Point-in-time reconstruction</text>
</svg>
''')


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "assets" / "architecture.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(), encoding="utf-8")
    print(path)
