"""Recreate the project architecture illustration (SVG)."""
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "assets" / "architecture.svg"
out.parent.mkdir(parents=True, exist_ok=True)
svg = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="130">
<rect width="800" height="130" fill="#f2f6ff"/>
<text x="20" y="70" font-size="22" fill="#123456">JSON samples → Contract engine → Policy gate → SQLite</text>
</svg>"""
out.write_text(svg + "\n", encoding="utf-8")
