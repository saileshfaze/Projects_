import json
from hydrograph.report import svg,write_json
from hydrograph.solver import solve

def test_svg(network):
    text=svg(network,solve(network));assert text.startswith('<svg') and 'R-A' in text
def test_json(tmp_path):
    p=tmp_path/'nested'/'a.json';write_json(p,{'ok':True});assert json.loads(p.read_text())['ok']
