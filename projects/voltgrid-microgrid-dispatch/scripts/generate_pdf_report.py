"""Generate a local PDF summary from a CLI dispatch result (optional reportlab)."""
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python scripts/generate_pdf_report.py INPUT_JSON OUTPUT_PDF")
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as exc:
        raise SystemExit("Install PDF support: pip install -e '.[reports]'") from exc
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = payload.get("result", payload)
    totals = result["totals"]
    styles = getSampleStyleSheet()
    story = [Paragraph("VoltGrid Dispatch Summary", styles["Title"]), Spacer(1, 12),
             Paragraph(str(result["scenario_name"]), styles["Heading2"])]
    values = [
        ["Metric", "Value"],
        ["Total cost (USD)", f"{totals['total_cost_usd']:.2f}"],
        ["Peak import (kW)", f"{totals['peak_import_kw']:.2f}"],
        ["Carbon (kg CO2)", f"{totals['carbon_kg']:.2f}"],
        ["Import (kWh)", f"{totals['import_kwh']:.2f}"],
        ["Solar curtailed (kWh)", f"{totals['curtailed_kwh']:.2f}"],
    ]
    table = Table(values, colWidths=[250, 170])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6eff8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(table)
    destination = Path(sys.argv[2])
    destination.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(destination), pagesize=A4).build(story)
    print(destination)

if __name__ == "__main__":
    main()
