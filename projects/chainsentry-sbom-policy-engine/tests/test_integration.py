import subprocess
import sys
from pathlib import Path


def test_synthetic_generator_reproducible():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "scripts/check_reproducibility.py")],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "Verified" in result.stdout


def test_demo_runs():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "scripts/demo.py")],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '"status": "fail"' in result.stdout
