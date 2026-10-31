from queryweaver.service import analyze, DEFAULT_SQL
from queryweaver.cli import main


def test_analyze():
    result = analyze(DEFAULT_SQL, seed=13, run=True)
    assert result["actual_rows"] <= 25
    assert result["optimized_cost"] > 0


def test_json_cli(capsys):
    assert main(["--format", "json"]) == 0
    assert '"plan"' in capsys.readouterr().out


def test_dot_cli(capsys):
    assert main(["--format", "dot"]) == 0
    assert "digraph" in capsys.readouterr().out


def test_export_cli(tmp_path):
    assert main(["--export-data", str(tmp_path)]) == 0
    assert (tmp_path / "orders.csv").exists()


def test_service_equivalence():
    sql = "SELECT c.id FROM customers c JOIN orders o ON c.id=o.customer_id"
    assert analyze(sql, run=True)["equivalent_to_baseline"]
