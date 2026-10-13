"""Render a PDF report from an evaluation JSON (requires reportlab)."""
import json
import sys
from pathlib import Path


def main():
    source, destination = map(Path, sys.argv[1:3])
    report = json.loads(source.read_text(encoding="utf-8"))
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    rows = [["Severity", "Code", "Path"]]
    rows += [[item["severity"], item["code"], item["path"]] for item in report["changes"]]
    if len(rows) == 1:
        rows.append(["info", "No structural changes", "$"])
    SimpleDocTemplate(str(destination), pagesize=A4).build([
        Paragraph("VectorGuard Regression Report", styles["Title"]),
        Paragraph("Verdict: " + report["verdict"].upper(), styles["Heading2"]),
        Table(rows, repeatRows=1),
    ])


if __name__ == "__main__":
    main()
