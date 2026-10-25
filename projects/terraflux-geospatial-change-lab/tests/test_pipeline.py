import json
from terraflux.pipeline import analyze
from terraflux.models import Settings


def test_pipeline_reports_area_and_patches(pair):
    before, after, _ = pair
    report = analyze(before, after)
    assert report['summary']['changed_pixels'] > 0
    assert report['summary']['changed_area_m2'] == report['summary']['changed_pixels']*100
    assert report['summary']['patch_count'] >= 2
    assert report['geojson']['type'] == 'FeatureCollection'


def test_report_is_deterministic(pair):
    before, after, _ = pair
    assert json.dumps(analyze(before, after), sort_keys=True) == json.dumps(analyze(before, after), sort_keys=True)


def test_high_threshold_suppresses_changes(pair):
    before, after, _ = pair
    report = analyze(before, after, Settings(ndvi_drop=1, nbr_drop=1))
    assert report['summary']['changed_pixels'] == 0


def test_small_components_filtered(pair):
    before, after, _ = pair
    report = analyze(before, after, Settings(min_patch_pixels=999999))
    assert report['summary']['patch_count'] == 0
