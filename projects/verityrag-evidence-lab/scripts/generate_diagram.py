"""Generate a standalone SVG without image dependencies."""
from pathlib import Path
from xml.sax.saxutils import escape

BOXES = [
    (24, "Synthetic corpus", "JSONL + SQLite"),
    (248, "Hybrid retrieval", "BM25 + char TF-IDF"),
    (472, "Evidence extraction", "filter + exact spans"),
    (696, "Evaluation", "MRR / nDCG / slices"),
]

def main():
    shapes = ['<svg xmlns="http://www.w3.org/2000/svg" width="910" height="220" viewBox="0 0 910 220">',
              '<rect width="910" height="220" fill="#f8fafc"/>',
              '<text x="24" y="42" font-size="23" font-family="Arial" fill="#0f172a">VerityRAG — evidence workflow</text>']
    for x, title, subtitle in BOXES:
        shapes.extend([f'<rect x="{x}" y="80" width="194" height="100" rx="10" fill="#e0f2fe" stroke="#0284c7"/>',
                       f'<text x="{x+12}" y="118" font-size="16" font-family="Arial" fill="#0c4a6e">{escape(title)}</text>',
                       f'<text x="{x+12}" y="145" font-size="12" font-family="Arial" fill="#075985">{escape(subtitle)}</text>'])
        if x != BOXES[-1][0]:
            shapes.append(f'<path d="M {x+194} 130 L {x+221} 130" stroke="#0f172a" stroke-width="2" marker-end="url(#arrow)"/>')
    shapes.insert(1, '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#0f172a"/></marker></defs>')
    shapes.append('</svg>')
    (Path(__file__).resolve().parents[1] / "assets/architecture.svg").write_text("\n".join(shapes) + "\n")

if __name__ == "__main__":
    main()
