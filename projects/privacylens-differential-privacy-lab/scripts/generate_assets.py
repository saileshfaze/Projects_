"""Create dependency-free architecture SVG."""
from pathlib import Path

def generate(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="170" viewBox="0 0 760 170"><rect width="760" height="170" fill="#0f172a"/><g font-family="Arial" font-size="18" text-anchor="middle" fill="white"><rect x="25" y="48" width="190" height="75" rx="10" fill="#2563eb"/><text x="120" y="90">Bound contributions</text><rect x="285" y="48" width="190" height="75" rx="10" fill="#0d9488"/><text x="380" y="90">Spend epsilon</text><rect x="545" y="48" width="190" height="75" rx="10" fill="#7c3aed"/><text x="640" y="90">Laplace release</text></g><path d="M215 85 H285 M475 85 H545" stroke="white" stroke-width="3"/><text x="380" y="25" font-family="Arial" font-size="19" text-anchor="middle" fill="white">PrivacyLens pipeline</text></svg>', encoding="utf-8")
if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "assets" / "pipeline.svg")
