from voltpilot.dispatch import simulate
from voltpilot.report import svg_soc,markdown,save_report


def test_svg_and_markdown(tmp_path,profile,site):
    summary,steps=simulate(profile,site)
    save_report(tmp_path,summary,steps,site.battery.capacity_kwh,"abc")
    assert "<svg" in (tmp_path/"soc.svg").read_text()
    assert "abc" in (tmp_path/"report.md").read_text()
    assert "synthetic" in markdown(summary)
