import json
import subprocess
import sys


def test_cli_returns_nonzero_on_regression(tmp_path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps([{"id": 1, "message": "accepted"}]), encoding="utf-8")
    new.write_text(json.dumps([{"id": "broken", "message": "rejected"}]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "app.cli", str(old), str(new)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["breaking"]


def test_cli_returns_zero_on_safe_update(tmp_path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps([{"id": 1}]), encoding="utf-8")
    new.write_text(json.dumps([{"id": 2, "added": True}]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "app.cli", str(old), str(new)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
