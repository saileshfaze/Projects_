# Local operations

`python scripts/run_demo.py` recreates a local demonstration in ignored `state/` and `reports/`. `python scripts/validate_assets.py` regenerates and checks that tracked synthetic CSVs are deterministic. The API uses `METRIFORGE_DB` and defaults to `state/metriforge.sqlite`.

Before changing synthetic generation, update both data and expected tests. A real factory integration would require a production data contract, access control, schema migrations, monitoring, calibration procedures, sample-rate handling, a documented baseline approval workflow and a manual decision path for lot release.
