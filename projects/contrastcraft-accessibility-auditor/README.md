# ContrastCraft — Accessibility Audit Lab

**Sailesh / saileshfaze** · MIT License · 2026

A dependency-light static HTML accessibility linter and WCAG 2.x contrast ratio calculator. Designed as a reproducible software-quality portfolio project.

## Quick start

```bash
python -m pip install -e .
contrastcraft audit data/issues.html --fail-on-errors
contrastcraft contrast '#222222' '#ffffff'
python -m pytest -q
python scripts/demo.py
```

The audit emits deterministic JSON findings with rule identifiers, severity and source line. The CLI exits nonzero when requested and errors exist. Included synthetic pages demonstrate valid and invalid cases.

## Checks

Document language/title; missing image alternatives; unlabeled form controls; duplicate IDs; unresolved ARIA references; empty buttons/links; anchors without href; image-input alt; disabled viewport zoom; deprecated font elements. Contrast is computed from sRGB relative luminance and WCAG 2.x thresholds (AA/AAA; normal/large text).

## Architecture

`colors.py` performs color parsing and contrast mathematics. `audit.py` uses the standard-library HTMLParser and accumulates structural findings; `cli.py` exposes commands. All examples are synthetic and require no credentials.

## Limitations

Not a complete WCAG audit, browser renderer, CSS cascade evaluator, screen reader, accessibility tree, or legal compliance certification. Dynamic JS, accessible names through nested elements, CSS-generated content, and color opacity are not modeled. HTMLParser is not a standards-compliant DOM parser. Human testing and browser-based tooling remain necessary.

## Reproducibility

`python scripts/generate_report.py` regenerates `assets/report.json`. CI is a nested template and must be moved to repository-root `.github/workflows/` to activate. No deployment or third-party certification is claimed.
