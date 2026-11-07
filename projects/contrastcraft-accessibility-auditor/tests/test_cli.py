import json
from contrastcraft.cli import main

def test_contrast(capsys):
    assert main(['contrast','#000','#fff'])==0
    assert json.loads(capsys.readouterr().out)['aa']

def test_audit(tmp_path,capsys):
    p=tmp_path/'a.html';p.write_text('<html lang="en"><title>ok</title></html>')
    assert main(['audit',str(p),'--fail-on-errors'])==0
    assert json.loads(capsys.readouterr().out)['count']==0

def test_fail(tmp_path):
    p=tmp_path/'a.html';p.write_text('<img>')
    assert main(['audit',str(p),'--fail-on-errors'])==1
