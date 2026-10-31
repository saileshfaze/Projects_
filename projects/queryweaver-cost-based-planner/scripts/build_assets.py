"""Regenerate the architecture diagram and query-plan DOT fixture."""
from pathlib import Path
from queryweaver.service import DEFAULT_SQL, analyze

ARCH = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="240" viewBox="0 0 1000 240">
<rect width="1000" height="240" fill="#f8fafc"/>
<text x="500" y="35" font-size="24" text-anchor="middle" fill="#0f172a" font-family="Arial">QueryWeaver architecture</text>
<g font-family="Arial" font-size="18" text-anchor="middle" fill="#0f172a">
<rect x="25" y="80" width="170" height="90" rx="12" fill="#dbeafe" stroke="#2563eb"/><text x="110" y="118">SQL lexer</text><text x="110" y="143">and parser</text>
<rect x="225" y="80" width="170" height="90" rx="12" fill="#dcfce7" stroke="#16a34a"/><text x="310" y="118">Statistics</text><text x="310" y="143">catalog</text>
<rect x="425" y="80" width="170" height="90" rx="12" fill="#fef3c7" stroke="#d97706"/><text x="510" y="118">DP join</text><text x="510" y="143">optimizer</text>
<rect x="625" y="80" width="170" height="90" rx="12" fill="#f3e8ff" stroke="#9333ea"/><text x="710" y="118">Reference</text><text x="710" y="143">executor</text>
<rect x="825" y="80" width="150" height="90" rx="12" fill="#fee2e2" stroke="#dc2626"/><text x="900" y="118">API / CLI</text><text x="900" y="143">reports</text>
</g><g stroke="#475569" stroke-width="3"><path d="M195 125 H225 M395 125 H425 M595 125 H625 M795 125 H825"/></g>
<text x="500" y="211" font-size="14" text-anchor="middle" fill="#64748b" font-family="Arial">Deterministic synthetic data • no production SQL execution • Sailesh 2026</text>
</svg>
'''


def main():
    out = Path("assets")
    out.mkdir(exist_ok=True)
    (out / "architecture.svg").write_text(ARCH, encoding="utf-8")
    (out / "example-plan.dot").write_text(analyze(DEFAULT_SQL)["dot"] + "
", encoding="utf-8")
    print("Generated assets/architecture.svg and assets/example-plan.dot")


if __name__ == "__main__":
    main()
