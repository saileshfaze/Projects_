"""Reproducibly generate an SVG diagram without binary dependencies."""
from pathlib import Path
Path('assets').mkdir(exist_ok=True)
Path('assets/architecture.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="560" height="90"><rect width="560" height="90" fill="#eef"/><text x="20" y="48" font-size="20">Input → Domain Engine → API</text></svg>')
