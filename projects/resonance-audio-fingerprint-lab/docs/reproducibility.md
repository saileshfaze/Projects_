# Reproducibility

Run `python scripts/generate_fixtures.py` to create five deterministic synthetic PCM WAV files, a SHA-256 manifest and an SVG spectrogram. Run with `--check` to compare exact bytes against generated expectations. The generator seeds NumPy's PCG64 random number generator explicitly.

`python scripts/validate_fixtures.py` checks SHA-256 and sample-rate/duration metadata. `python scripts/demo.py` demonstrates ingest and search. `python scripts/benchmark.py` measures local runtime but is not a representative performance benchmark. Use `pytest -q` for regression coverage.

The SVG and WAV files are derived artifacts. Their deterministic generation depends on NumPy behavior and floating-point implementation; pin a build environment when bit-for-bit reproducibility across machines is required.
