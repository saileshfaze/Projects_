"""Export a self-contained SVG and HTML dispatch report."""
import argparse
import json
from pathlib import Path
from routeforge.ingest import load_problem
from routeforge.reporting import render_html, render_svg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("plan")
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    problem = load_problem(args.problem)
    plan = json.loads(Path(args.plan).read_text())
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "routes.svg").write_text(render_svg(problem, plan), encoding="utf-8")
    (folder / "report.html").write_text(render_html(problem, plan), encoding="utf-8")
    print(folder)

if __name__ == "__main__":
    main()
