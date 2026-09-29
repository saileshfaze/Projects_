# SentinelStream Risk Platform

Portfolio-grade real-time transaction anomaly detection and operational risk platform. It validates events, computes behavioral features, combines explainable rules with Isolation Forest anomaly scoring, persists decisions, exposes analytics APIs, and publishes Prometheus metrics.

## Stack
Python 3.12, FastAPI, Pydantic, scikit-learn, NumPy, SQLAlchemy, Prometheus, pytest, Docker, GitHub Actions.

## Quick start
```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/generate_dataset.py
uvicorn app.main:app --reload
```
Open `http://localhost:8000/docs`. Use `POST /v1/score` and `GET /v1/analytics/summary`.

Highlights: typed contracts, hybrid ML + rules, explainable reason codes, idempotent persistence, observability, synthetic dataset generation, tests, containerization, CI, architecture decisions, and security notes. No credentials or real financial data are included.
