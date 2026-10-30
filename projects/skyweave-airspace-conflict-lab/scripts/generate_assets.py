"""Generate reproducible SVG visualization from the synthetic crossing scenario."""
from pathlib import Path
from skyweave.scenarios import crossing
from skyweave.detector import detect
from skyweave.reporting import timeline_svg

root=Path(__file__).resolve().parents[1]
(root/'assets'/'crossing-timeline.svg').write_text(timeline_svg(detect(crossing())))
print('Generated assets/crossing-timeline.svg')
