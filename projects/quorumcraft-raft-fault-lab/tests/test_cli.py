import json
from quorumcraft.cli import main


def test_generate_cli(tmp_path):
    path = tmp_path / "generated.json"
    assert main(["generate", "--output", str(path)]) == 0
    assert json.loads(path.read_text())["nodes"] == 5


def test_demo_cli(tmp_path):
    output, svg = tmp_path / "run.json", tmp_path / "plot.svg"
    assert main(["demo", "--output", str(output), "--svg", str(svg)]) == 0
    assert output.exists() and svg.exists()
    assert main(["verify", str(output)]) == 0


def test_scenario_cli(tmp_path):
    scenario, output = tmp_path / "scenario.json", tmp_path / "out.json"
    main(["generate", "--output", str(scenario)])
    assert main(["scenario", str(scenario), "--output", str(output)]) == 0
    assert json.loads(output.read_text())["metrics"]["audit_valid"]
