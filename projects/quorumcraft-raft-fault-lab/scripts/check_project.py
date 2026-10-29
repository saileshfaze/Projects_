"""Lightweight packaging and secret-placeholder validation."""
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    required = ["README.md", "LICENSE", "pyproject.toml", ".env.example", "Dockerfile", "compose.yaml",
                ".github/workflows/ci.yml", "data/partition-heal.json", "assets/leadership-timeline.svg"]
    missing = [item for item in required if not (root / item).is_file()]
    assert not missing, f"missing required files: {missing}"
    assert "Copyright (c) 2026 Sailesh" in (root / "LICENSE").read_text()
    assert not (root / ".env").exists(), "never commit a real .env"
    print("Project structure and MIT license validated")


if __name__ == "__main__":
    main()
