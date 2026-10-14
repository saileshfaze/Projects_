"""Rebuild the checked-in SVG and optionally generate a PDF architecture summary."""

import argparse
from pathlib import Path

SVG = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"960\" height=\"150\" viewBox=\"0 0 960 150\" role=\"img\" aria-label=\"AtlasFlow ML Orchestrator architecture\"><rect width=\"960\" height=\"150\" fill=\"#f8fafc\"/><g font-family=\"sans-serif\" font-size=\"18\" fill=\"#0f172a\"><rect x=\"12\" y=\"45\" width=\"198\" height=\"60\" rx=\"12\" fill=\"#dbeafe\" stroke=\"#2563eb\"/><text x=\"31\" y=\"82\">Dataset + digest</text><text x=\"224\" y=\"82\">→</text><rect x=\"257\" y=\"45\" width=\"191\" height=\"60\" rx=\"12\" fill=\"#dcfce7\" stroke=\"#16a34a\"/><text x=\"276\" y=\"82\">Experiment run</text><text x=\"462\" y=\"82\">→</text><rect x=\"493\" y=\"45\" width=\"194\" height=\"60\" rx=\"12\" fill=\"#fef9c3\" stroke=\"#ca8a04\"/><text x=\"513\" y=\"82\">Evaluation gates</text><text x=\"702\" y=\"82\">→</text><rect x=\"737\" y=\"45\" width=\"212\" height=\"60\" rx=\"12\" fill=\"#f3e8ff\" stroke=\"#9333ea\"/><text x=\"753\" y=\"82\">Champion registry</text></g></svg>"


def build_svg(destination: str = "assets/architecture.svg") -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SVG, encoding="utf-8")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="store_true", help="also generate a PDF (reportlab)")
    args = parser.parse_args()
    print(build_svg())
    if args.pdf:
        print(build_pdf())
