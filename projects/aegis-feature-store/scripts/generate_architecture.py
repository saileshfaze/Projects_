"""Regenerate a standalone SVG architecture diagram using the Python standard library."""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree


def build(output: Path):
    svg = Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": "1000", "height": "340", "viewBox": "0 0 1000 340",
        "role": "img",
    })
    SubElement(svg, "title").text = "Aegis Feature Store Architecture"
    SubElement(svg, "rect", {"width": "1000", "height": "340", "fill": "#f8fafc"})
    title = SubElement(svg, "text", {
        "x": "40", "y": "45", "font-family": "Arial", "font-size": "25",
        "fill": "#0f172a",
    })
    title.text = "Aegis Feature Store"
    blocks = [
        (40, 110, 190, 80, "Feature registry", "#dbeafe"),
        (40, 220, 190, 80, "Event ingestion", "#dbeafe"),
        (310, 150, 245, 110, "SQLite feature history", "#ccfbf1"),
        (645, 100, 290, 80, "Offline as-of joins", "#fef3c7"),
        (645, 220, 290, 80, "Online materialization", "#fce7f3"),
    ]
    for x, y, w, h, label, fill in blocks:
        SubElement(svg, "rect", {
            "x": str(x), "y": str(y), "width": str(w), "height": str(h),
            "rx": "12", "fill": fill, "stroke": "#475569", "stroke-width": "2",
        })
        node = SubElement(svg, "text", {
            "x": str(x + w // 2), "y": str(y + h // 2),
            "text-anchor": "middle", "font-family": "Arial", "font-size": "17",
            "fill": "#0f172a",
        })
        node.text = label
    for coordinates in ("230,150 310,185", "230,260 310,225",
                        "555,180 645,140", "555,230 645,260"):
        x1, y1, x2, y2 = coordinates.replace(" ", ",").split(",")
        SubElement(svg, "line", {
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "stroke": "#475569", "stroke-width": "3",
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    ElementTree(svg).write(output, encoding="utf-8", xml_declaration=True)
    print(f"Generated {output}")


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1] / "assets" / "architecture.svg")
