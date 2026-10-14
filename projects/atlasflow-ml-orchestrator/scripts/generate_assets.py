"""Rebuild the original architecture SVG and optional PDF using local dependencies."""

from pathlib import Path


def build_svg(destination: str = "assets/architecture.svg") -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    nodes = ("Dataset + digest", "Experiment run", "Evaluation gates", "Champion registry")
    items = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="150">']
    items.append('<rect width="960" height="150" fill="#f8fafc"/>')
    for i, label in enumerate(nodes):
        x = 12 + i * 240
        items.append(f'<rect x="{x}" y="40" width="215" height="70" rx="10" fill="#dbeafe" stroke="#2563eb"/>')
        items.append(f'<text x="{x + 12}" y="80" font-family="sans-serif" font-size="17">{label}</text>')
    items.append("</svg>")
    target.write_text("".join(items), encoding="utf-8")
    return target


def build_pdf(destination: str = "assets/architecture.pdf") -> Path:
    try:
        from reportlab.pdfgen import canvas
    except ImportError as error:
        raise RuntimeError("Install reportlab to generate the optional PDF") from error
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    page = canvas.Canvas(str(target))
    page.setFont("Helvetica-Bold", 18)
    page.drawString(45, 790, "AtlasFlow ML Orchestrator")
    page.setFont("Helvetica", 12)
    page.drawString(45, 740, "Dataset -> Experiment -> Quality gates -> Champion")
    page.save()
    return target


if __name__ == "__main__":
    print(build_svg())
    print(build_pdf())
