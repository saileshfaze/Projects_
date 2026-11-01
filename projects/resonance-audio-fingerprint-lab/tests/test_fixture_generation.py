import importlib.util
from pathlib import Path

def test_generated_fixture_manifest():
    path=Path(__file__).resolve().parents[1]/"scripts/generate_fixtures.py"
    spec=importlib.util.spec_from_file_location("fixtures",path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    outputs=mod.generate()
    assert "data/manifest.json" in outputs
    assert len(outputs)==7
    assert outputs["data/melody_a.wav"][:4]==b"RIFF"
