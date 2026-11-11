import json
import pytest
from packetforge.wire import Frame
from packetforge.trace import export_trace,import_trace
from packetforge.errors import FrameError
from packetforge.cli import main

def test_trace_roundtrip():
    frames=[Frame(1,i,b'data') for i in range(5)]
    assert import_trace(export_trace(frames))==frames

def test_trace_tamper():
    data=json.loads(export_trace([Frame(1,1,b'data')]));data[0]['kind']=2
    with pytest.raises(FrameError):import_trace(json.dumps(data))

def test_trace_bad_list():
    with pytest.raises(FrameError):import_trace('{}')

def test_trace_bad_record():
    with pytest.raises(FrameError):import_trace('[{}]')

def test_cli_encode(capsys):
    main(['encode','hello','--sequence','7']);assert capsys.readouterr().out.startswith('5046')

def test_cli_campaign(capsys):
    main(['campaign','--seed','123','--cases','10']);r=json.loads(capsys.readouterr().out);assert r['cases']==10

def test_cli_trace(tmp_path):
    out=tmp_path/'sub'/'trace.json';main(['trace','--output',str(out)])
    assert len(import_trace(out.read_text()))==5

def test_cli_output(tmp_path):
    out=tmp_path/'report.json';main(['campaign','--cases','5','--output',str(out)])
    assert json.loads(out.read_text())['cases']==5
