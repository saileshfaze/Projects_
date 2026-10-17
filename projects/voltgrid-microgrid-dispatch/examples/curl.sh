#!/usr/bin/env sh
set -eu
curl -fsS http://127.0.0.1:8000/healthz
curl -fsS -X POST http://127.0.0.1:8000/v1/dispatches \
  -H 'Content-Type: application/json' \
  --data @data/demo_scenario.json
