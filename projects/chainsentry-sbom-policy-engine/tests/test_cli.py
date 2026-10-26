import json
from chainsentry.cli import main


def test_cli_failure_exit_code(capsys, tmp_path):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "examples"
    code = main(["scan", "--sbom", str(root / "cyclonedx.json"), "--feed", str(root / "advisories.json"),
                 "--policy", str(root / "policy.json"), "--db", str(tmp_path / "test.db")])
    assert code == 2
    assert json.loads(capsys.readouterr().out)["scan_id"] == 1


def test_cli_missing_file(capsys):
    assert main(["scan", "--sbom", "missing", "--feed", "missing", "--policy", "missing"]) == 1
    assert "chainsentry:" in capsys.readouterr().err
