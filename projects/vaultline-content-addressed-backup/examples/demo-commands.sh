#!/bin/sh
set -eu
python scripts/generate_fixture.py sample-output/source --seed 42 --files 24
vaultline --vault sample-output/vault snapshot sample-output/source --label sample
vaultline --vault sample-output/vault list
vaultline --vault sample-output/vault audit
vaultline --vault sample-output/vault report sample-output/inventory.svg
