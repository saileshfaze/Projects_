"""Generate an SVG architecture overview using only the Python standard library."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "assets" / "architecture.svg"
out.parent.mkdir(exist_ok=True)
labels = ["CSV / JSON", "Pydantic validation", "HiGHS MILP", "FastAPI + SQLite"]
shapes = []
for index, label in enumerate(labels):
    x = 30 + 270 * index
    shapes.append(
        f'<rect x="{x}" y="90" width="230" height="90" rx="12" fill="#c9ecff"/>'
        f'<text x="{x + 115}" y="143" font-size="18" fill="#17324d" '
        f'font-family="sans-serif" text-anchor="middle">{escape(label)}</text>'
    )
    if index < 3:
        shapes.append(f'<path d="M{x+230} 135H{x+270}" stroke="#fff" stroke-width="4"/>')
out.write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="230" '
    'viewBox="0 0 1100 230"><rect width="1100" height="230" fill="#102239"/>'
    '<text x="30" y="48" fill="white" font-family="sans-serif" font-size="28">'
    'VoltGrid Architecture</text>' + "".join(shapes) + '</svg>', encoding="utf-8"
)
print(out)
