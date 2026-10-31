"""In-process API smoke test without requiring a running server."""
from queryweaver.api import PlanRequest, health, plan


def main():
    assert health()["status"] == "ok"
    result = plan(PlanRequest(sql="SELECT * FROM customers c LIMIT 2", execute=True))
    assert result["actual_rows"] == 2
    print("PASS: API health and planning handlers")


if __name__ == "__main__":
    main()
