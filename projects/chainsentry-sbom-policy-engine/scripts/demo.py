"""Run an end-to-end local demonstration and print a concise JSON report."""
import json
from pathlib import Path
from chainsentry import scan

root = Path(__file__).resolve().parents[1] / "examples"
read = lambda name: json.loads((root / name).read_text())
result = scan(read("cyclonedx.json"), read("advisories.json"), read("policy.json"))
print(json.dumps(result.to_dict(), indent=2))
