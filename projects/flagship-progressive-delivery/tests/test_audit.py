import json
from flagship.audit import append,verify

def test_chain(tmp_path):
    p=str(tmp_path/'audit.jsonl')
    append(p,{'type':'exposure'});append(p,{'type':'conversion'})
    assert verify(p)

def test_tampering(tmp_path):
    p=tmp_path/'audit.jsonl';append(str(p),{'type':'exposure'})
    p.write_text(p.read_text().replace('exposure','fabricated'))
    assert not verify(str(p))
