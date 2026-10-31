import pytest


def test_health():
    from queryweaver.api import health
    assert health()["status"] == "ok"


def test_api_plan():
    from queryweaver.api import plan, PlanRequest
    result = plan(PlanRequest(sql="SELECT * FROM customers c", execute=True))
    assert result["actual_rows"] == 120


def test_api_invalid():
    from fastapi import HTTPException
    from queryweaver.api import plan, PlanRequest
    with pytest.raises(HTTPException) as exc:
        plan(PlanRequest(sql="DROP TABLE customers"))
    assert exc.value.status_code == 422
