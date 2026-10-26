"""Produce an editable SVG overview without third-party drawing dependencies."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "architecture.svg"


def render() -> None:
    blocks = ["CycloneDX / SPDX", "Normalize & Validate", "Graph Reachability", "Advisory + Policy", "Findings + Drift"]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="200" viewBox="0 0 1160 200">',
             '<rect width="1160" height="200" fill="#f8fafc"/>',
             '<text x="24" y="35" font-size="23" fill="#0f172a" font-family="sans-serif">ChainSentry · offline analysis pipeline</text>']
    for i, label in enumerate(blocks):
        x = 20 + 232 * i
        parts.append(f'<rect x="{x}" y="72" rx="9" width="206" height="74" fill="#e0f2fe" stroke="#0369a1"/>')
        parts.append(f'<text x="{x+103}" y="115" text-anchor="middle" font-size="15" fill="#0f172a" font-family="sans-serif">{label.replace("&", "&amp;")}</text>')
        if i < len(blocks)-1:
            parts.append(f'<path d="M {x+206} 109 h 25" stroke="#0369a1" stroke-width="2"/>')
    parts.append('</svg>')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
