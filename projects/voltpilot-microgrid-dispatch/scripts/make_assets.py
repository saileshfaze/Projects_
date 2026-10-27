"""Generate an example SOC SVG without graphics dependencies."""
from pathlib import Path
from voltpilot.synthetic import generate
from voltpilot.models import Site
from voltpilot.dispatch import simulate
from voltpilot.report import svg_soc


def main():
    site=Site()
    _,steps=simulate(generate(days=1),site)
    path=Path("assets/sample-soc.svg")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(svg_soc(steps,site.battery.capacity_kwh),encoding="utf-8")
    print(path)


if __name__=="__main__": main()
