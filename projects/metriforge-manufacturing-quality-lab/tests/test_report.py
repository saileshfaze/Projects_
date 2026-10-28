import json
from metriforge.engine import evaluate
from metriforge.report import svg_chart,save_json,save_svg

def test_svg(scenario,spec):
    svg=svg_chart(evaluate(*scenario[:2],spec));assert svg.startswith('<svg') and 'polyline' in svg
def test_file_outputs(tmp_path,scenario,spec):
    report=evaluate(*scenario[:2],spec)
    save_json(report,str(tmp_path/'report.json'));save_svg(report,str(tmp_path/'chart.svg'))
    assert json.loads((tmp_path/'report.json').read_text())['production_count']==120
    assert (tmp_path/'chart.svg').read_text().endswith('</svg>\n')
