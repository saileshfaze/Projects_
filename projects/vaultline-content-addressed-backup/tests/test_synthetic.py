from vaultline.synthetic import generate
from vaultline.report import svg_report
from vaultline.engine import Vault

def test_reproducible(tmp_path):
    a=tmp_path/"a"; b=tmp_path/"b"
    assert generate(a, seed=5, files=17) == 17
    assert generate(b, seed=5, files=17) == 17
    assert [(p.relative_to(a),p.read_bytes()) for p in sorted(a.rglob("*.csv"))] == [(p.relative_to(b),p.read_bytes()) for p in sorted(b.rglob("*.csv"))]

def test_report(tmp_path):
    v=Vault(tmp_path/"vault")
    svg=svg_report(v)
    assert "Vaultline storage inventory" in svg
    assert "Snapshots: 0" in svg
