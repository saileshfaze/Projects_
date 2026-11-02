import json
from vaultline.cli import main

def test_cli_workflow(sample, capsys):
    root, source, vault=sample
    assert main(["--vault", str(vault.root), "snapshot", str(source), "--label", "demo"]) == 0
    snap=json.loads(capsys.readouterr().out)
    assert main(["--vault", str(vault.root), "verify", snap["id"]]) == 0
    assert json.loads(capsys.readouterr().out)["ok"]
    assert main(["--vault", str(vault.root), "restore", snap["id"], str(root/"restored")]) == 0
    capsys.readouterr()
    assert main(["--vault", str(vault.root), "audit"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"]

def test_cli_bad_identifier(sample):
    root, source, vault=sample
    assert main(["--vault", str(vault.root), "verify", "bad"]) == 2

def test_cli_report(sample):
    root, source, vault=sample
    vault.snapshot(source)
    output=root/"report.svg"
    assert main(["--vault", str(vault.root), "report", str(output)]) == 0
    assert "<svg" in output.read_text()
