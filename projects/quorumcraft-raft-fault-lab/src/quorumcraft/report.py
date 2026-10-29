"""Portable SVG visualization; no plotting dependency required."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .raft import Cluster


def timeline_svg(cluster: Cluster, width: int = 1000) -> str:
    height = 270
    ticks = cluster.timeline
    n = max(1, len(ticks))
    leaders = sorted(cluster.nodes)
    colors = {node: color for node, color in zip(leaders,
              ["#2563eb", "#059669", "#d97706", "#9333ea", "#dc2626", "#0891b2", "#7c3aed"])}
    chart_width = width - 110
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Raft leader timeline">',
              '<rect width="100%" height="100%" fill="#0b1220"/>',
              '<text x="35" y="34" fill="white" font-size="20" font-family="sans-serif">QuorumCraft · Leadership Timeline</text>',
              '<text x="35" y="55" fill="#94a3b8" font-size="11" font-family="sans-serif">Deterministic simulation · synthetic network</text>']
    for index, point in enumerate(ticks):
        x = 55 + index * chart_width / n
        cell_width = chart_width / n + 0.4
        leader = point["leader"]
        color = colors.get(leader, "#475569")
        pieces.append(f'<rect x="{x:.2f}" y="83" width="{cell_width:.2f}" height="85" fill="{color}"/>')
        if point["blocked_links"]:
            pieces.append(f'<rect x="{x:.2f}" y="175" width="{cell_width:.2f}" height="17" fill="#f43f5e"/>')
    pieces.extend(['<text x="55" y="215" fill="#94a3b8" font-size="12" font-family="sans-serif">Red strip = partition active</text>',
                   f'<text x="55" y="238" fill="#94a3b8" font-size="12" font-family="sans-serif">0 to {cluster.now} simulated ticks</text>'])
    for index, leader in enumerate(leaders):
        x = 480 + (index % 4) * 115
        y = 215 + (index // 4) * 22
        pieces.append(f'<rect x="{x}" y="{y-10}" width="10" height="10" fill="{colors.get(leader, "#0891b2")}"/>')
        pieces.append(f'<text x="{x+15}" y="{y}" fill="#e2e8f0" font-size="12" font-family="sans-serif">{escape(leader)}</text>')
    pieces.append('</svg>')
    return "\n".join(pieces) + "\n"


def write_report(cluster: Cluster, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(timeline_svg(cluster), encoding="utf-8")
    return path
