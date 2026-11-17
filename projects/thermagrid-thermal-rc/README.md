# ThermaGrid — Building Thermal Dynamics Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · Synthetic engineering portfolio

A reproducible first-order resistance-capacitance (RC) model for indoor temperature, heat transfer, internal gains, thermostat heating/cooling, and time-varying electricity tariffs. Compares thermostat and uncontrolled trajectories using explicit Euler integration with a conservative time-step guard. No external service or personal data.

## Run

```bash
pip install -e . --no-build-isolation
pytest -q
python scripts/generate.py --hours 48 --seed 2026
thermagrid data/generated.json --output artifacts/report.json
```

See `docs/model.md` for the equations and `docs/limitations.md` for assumptions. Synthetic data and output do not represent measured building performance.
