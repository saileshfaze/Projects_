"""Regenerate architecture SVG without nonstandard dependencies."""
from pathlib import Path
from xml.sax.saxutils import escape


def main() -> None:
    labels=["HMAC allocation", "SQLite ledger", "CUPED + bootstrap", "Guardrails + API"]
    rectangles=[]
    for i,label in enumerate(labels):
        x=20+i*200
        rectangles.append(f'<rect x="{x}" y="40" width="175" height="70" rx="12" fill="#123454" stroke="#61d0cc" stroke-width="2"/>')
        rectangles.append(f'<text x="{x+87}" y="80" text-anchor="middle" fill="white" font-family="Arial" font-size="14">{escape(label)}</text>')
        if i:
            rectangles.append(f'<path d="M{x-25} 75 L{x-5} 75" stroke="#61d0cc" stroke-width="3"/>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="820" height="150" viewBox="0 0 820 150"><rect width="820" height="150" fill="#071c2d"/>'+''.join(rectangles)+'</svg>'
    path=Path(__file__).resolve().parents[1]/"assets"/"architecture.svg"
    path.write_text(svg,encoding="utf-8")
    print(path)


if __name__=="__main__":
    main()
