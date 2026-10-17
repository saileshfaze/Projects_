"""Static HTML dispatch report with escaped user-controlled scenario labels."""

from html import escape

def html_report(result: dict) -> str:
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(str(row[k]))}</td>" for k in
            ("timestamp", "grid_import_kw", "grid_export_kw", "soc_kwh")) + "</tr>"
        for row in result["schedule"]
    )
    totals = result["totals"]
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<title>VoltGrid Dispatch Report</title>"
        "<style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;color:#17324d}"
        "table{border-collapse:collapse;width:100%}td,th{padding:.6rem;border:1px solid #cad5df}"
        "th{background:#e8f2fa}h1{color:#123b60}</style>"
        f"<h1>{escape(str(result['scenario_name']))}</h1>"
        f"<p>Total cost: ${totals['total_cost_usd']:.2f} | "
        f"Carbon: {totals['carbon_kg']:.2f} kg CO₂ | "
        f"Peak: {totals['peak_import_kw']:.2f} kW</p>"
        "<table><thead><tr><th>Time</th><th>Import kW</th>"
        "<th>Export kW</th><th>SOC kWh</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></html>"
    )
