from quorumcraft import Cluster
from quorumcraft.metrics import evaluate
from quorumcraft.persistence import export_run, verify_export
from quorumcraft.report import timeline_svg, write_report


def test_empty_metrics():
    assert evaluate(Cluster())["leader_available_fraction"] == 0


def test_metrics_with_leader(elected):
    assert evaluate(elected)["leader_available_fraction"] > 0


def test_export_and_verify(tmp_path, elected):
    path = export_run(elected, tmp_path / "run.json")
    assert path.exists()
    assert verify_export(path)


def test_tampered_export_fails(tmp_path, elected):
    import json
    path = export_run(elected, tmp_path / "run.json")
    data = json.loads(path.read_text())
    data["audit"][0]["action"] = "forged"
    path.write_text(json.dumps(data))
    assert not verify_export(path)


def test_svg_rendering(elected):
    svg = timeline_svg(elected)
    assert svg.startswith('<svg xmlns=')
    assert "Leadership Timeline" in svg


def test_write_report(tmp_path, elected):
    path = write_report(elected, tmp_path / "report.svg")
    assert path.read_text().endswith("</svg>\n")
