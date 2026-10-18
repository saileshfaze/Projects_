from routeforge.optimizer import optimize
from routeforge.reporting import render_svg, render_html

def test_svg(problem):
    svg = render_svg(problem, optimize(problem))
    assert svg.startswith("<svg")
    assert "CE-001" in svg
    assert "</svg>" in svg

def test_html(problem):
    html = render_html(problem, optimize(problem))
    assert "<!doctype html>" in html
    assert "RouteForge dispatch report" in html
