"""Generate an SVG architecture diagram with no external drawing dependencies."""
from pathlib import Path


def main() -> None:
    nodes = [(20,"Synthetic / NPZ scenes"),(230,"Contracts & QA masks"),
             (440,"NDVI + NBR deltas"),(650,"Connected components"),
             (860,"GeoJSON + uncertainty"),(1070,"SQLite / REST API")]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1290" height="180" viewBox="0 0 1290 180">',
           '<rect width="1290" height="180" fill="#f5f8fc"/>',
           '<text x="20" y="35" font-family="Arial" font-size="23" fill="#142c43">TerraFlux · Change screening pipeline</text>']
    for x, label in nodes:
        out.append(f'<rect x="{x}" y="75" width="190" height="70" rx="9" fill="#173c55"/>')
        out.append(f'<text x="{x+95}" y="116" text-anchor="middle" font-family="Arial" font-size="13" fill="white">{label.replace("&","&amp;")}</text>')
        if x < 1070:
            out.append(f'<path d="M{x+190} 110 h20" stroke="#159e9c" stroke-width="3"/>')
    out.append('</svg>')
    p = Path("assets/architecture.svg")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out)+"\n", encoding="utf-8")
    print(p)


if __name__ == "__main__":
    main()
