import json
from skyweave.cli import main
from skyweave.models import flights_payload
from skyweave.scenarios import crossing

def test_cli(tmp_path,capsys):
    source=tmp_path/'input.json';source.write_text(json.dumps(flights_payload(crossing())))
    main([str(source),'--out',str(tmp_path/'out'),'--db',str(tmp_path/'db.sqlite'),'--samples','3'])
    out=tmp_path/'out'
    assert all((out/f).exists() for f in ('report.json','tracks.geojson','conflicts.csv','timeline.svg'))
    assert json.loads((out/'report.json').read_text())['conflict_count']==1
