import json
from helixbench.analysis import analyze
from helixbench.cli import main

def test_report():
    result = analyze("ATGAAATAG")
    assert result["length"] == 9 and result["orfs"]
    json.dumps(result)
def test_cli(capsys):
    assert main(["analyze","--sequence","ATGAAATAG"]) == 0
    assert json.loads(capsys.readouterr().out)["length"] == 9
def test_fasta_cli(tmp_path,capsys):
    path = tmp_path / "fixture.fasta"
    path.write_text(">x\nATGAAATAG\n")
    assert main(["fasta",str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["x"]["length"] == 9
