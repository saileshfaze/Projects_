from causalpilot.models import Experiment
from causalpilot.synthetic import generate, read_csv, write_csv


def test_generator_reproducible(config):
    assert generate(config,10)==generate(config,10)


def test_csv_roundtrip(config,tmp_path):
    path=tmp_path/"events.csv"
    write_csv(generate(config,12),path)
    assert len(read_csv(path))==12
    assert read_csv(path)[0]==generate(config,12)[0]


def test_end_to_end(service,config):
    events=generate(config,100,seed=8)
    for event in events:
        assert service.ingest(event)
    report=service.report(config.experiment_id)
    assert report["observed"]["A"]+report["observed"]["B"]==100
    assert report["eligible"]
    assert report["revenue"]["draws"]==1200
    assert not report["srm"]["flag"]
