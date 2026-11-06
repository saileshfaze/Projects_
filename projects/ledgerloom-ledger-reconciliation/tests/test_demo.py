from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from demo import run
from generate_data import generate

def test_demo(tmp_path):
    result=run(tmp_path)
    assert result["audit_valid"] and result["matched"]==12
    assert (tmp_path/"report.json").exists()
    assert (tmp_path/"trial-balance.svg").exists()
def test_synthetic_deterministic(tmp_path):
    a=generate(tmp_path/"a.csv",seed=3,count=15)
    b=generate(tmp_path/"b.csv",seed=3,count=15)
    assert a.read_bytes()==b.read_bytes()
    assert len(a.read_text().splitlines())==16
