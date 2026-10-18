"""Self-contained SVG/HTML output; escape all user-provided identifiers."""
from html import escape
from .domain import Problem

def render_svg(problem: Problem, plan: dict, width: int = 760, height: int = 520) -> str:
    points = [(problem.depot.lat, problem.depot.lon)] + [(j.lat, j.lon) for j in problem.jobs]
    min_lat, max_lat = min(x for x, _ in points), max(x for x, _ in points)
    min_lon, max_lon = min(y for _, y in points), max(y for _, y in points)
    def xy(lat, lon):
        return (40 + (lon - min_lon) / max(max_lon - min_lon, 0.000001) * (width - 80),
                40 + (max_lat - lat) / max(max_lat - min_lat, 0.000001) * (height - 80))
    jobs = {j.id: j for j in problem.jobs}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + str(width) + ' ' + str(height) + '">',
           '<rect width="100%" height="100%" fill="#f7f9fc"/>']
    palette = ("#2563eb", "#db2777", "#059669", "#b45309", "#7c3aed")
    for i, route in enumerate(plan["routes"]):
        positions = [xy(problem.depot.lat, problem.depot.lon)] + [xy(jobs[j].lat, jobs[j].lon) for j in route["jobs"]]
        positions.append(positions[0])
        points_str = " ".join(str(round(x, 2)) + "," + str(round(y, 2)) for x, y in positions)
        out.append('<polyline points="' + points_str + '" fill="none" stroke="' + palette[i % len(palette)] + '" stroke-width="2.5"/>')
    for job in problem.jobs:
        x, y = xy(job.lat, job.lon)
        out.append('<circle cx="' + str(round(x, 2)) + '" cy="' + str(round(y, 2)) + '" r="5" fill="#0f172a"/>')
        out.append('<text x="' + str(round(x + 8, 2)) + '" y="' + str(round(y - 8, 2)) + '" font-size="12">' + escape(job.id) + '</text>')
    x, y = xy(problem.depot.lat, problem.depot.lon)
    out.append('<rect x="' + str(round(x - 7, 2)) + '" y="' + str(round(y - 7, 2)) + '" width="14" height="14" fill="#dc2626"/>')
    out.append('</svg>')
    return "\n".join(out)

def render_html(problem: Problem, plan: dict) -> str:
    svg = render_svg(problem, plan)
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><title>RouteForge report</title>'
            '<style>body{font:16px system-ui;max-width:1000px;margin:auto;padding:2rem;color:#172033}</style>'
            '<h1>RouteForge dispatch report</h1><p>Plan ' + escape(plan["plan_id"]) + '</p>'
            '<p>Served ' + str(plan["jobs_served"]) + ' / ' + str(plan["jobs_total"]) +
            ' jobs · Cost €' + str(plan["total_cost"]) + '</p>' + svg + '</html>')
