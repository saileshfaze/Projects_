from voltgrid.report import html_report

def test_escapes_scenario_name():
    report = html_report({
        "scenario_name": "<script>alert(1)</script>",
        "totals": {"total_cost_usd": 12.5, "carbon_kg": 3.2, "peak_import_kw": 4},
        "schedule": [{"timestamp": "2026-10-01", "grid_import_kw": 1,
                      "grid_export_kw": 0, "soc_kwh": 2}],
    })
    assert "&lt;script&gt;" in report
    assert "<script>" not in report
