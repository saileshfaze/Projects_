"""Self-contained SVG and Markdown reports, no external plotting service."""
from dataclasses import asdict
from pathlib import Path
from .models import Dispatch, Summary


def svg_soc(steps: list[Dispatch], capacity_kwh: float) -> str:
    if not steps or capacity_kwh <= 0:
        raise ValueError("steps and positive capacity required")
    w,h = 920,260
    pts = " ".join(f"{45+i*830/max(1,len(steps)-1):.2f},{215-x.soc_kwh/capacity_kwh*175:.2f}" for i,x in enumerate(steps))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Battery state of charge over time">'
            '<rect width="920" height="260" fill="#101827"/><line x1="45" y1="215" x2="875" y2="215" stroke="#a5b4c5"/>'
            f'<polyline fill="none" stroke="#35d4a2" stroke-width="3" points="{pts}"/>'
            f'<text x="45" y="25" fill="white" font-family="sans-serif">Battery SOC (0–{capacity_kwh:g} kWh)</text></svg>')


def markdown(summary: Summary, run_id: str = "local") -> str:
    rows = ["# VoltPilot dispatch report", "", f"Run: `{run_id}`", "", f"Strategy: **{summary.strategy}**", "", "| Metric | Value |", "|---|---:|"]
    for key,value in asdict(summary).items():
        if key in ("strategy",):
            continue
        rows.append(f"| {key.replace('_',' ')} | {value:.4f} |" if isinstance(value,float) else f"| {key.replace('_',' ')} | {value} |")
    rows += ["", "Results are from synthetic profiles; they are not utility bills or production forecasts.", ""]
    return "\n".join(rows)


def save_report(directory: str | Path, summary: Summary, steps: list[Dispatch], capacity_kwh: float, run_id: str) -> None:
    path=Path(directory);path.mkdir(parents=True,exist_ok=True)
    (path/"report.md").write_text(markdown(summary,run_id),encoding="utf-8")
    (path/"soc.svg").write_text(svg_soc(steps,capacity_kwh),encoding="utf-8")
