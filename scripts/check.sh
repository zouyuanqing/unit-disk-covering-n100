#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python scripts/verify_certificate.py
python scripts/generate_bounds.py
bash scripts/build-paper.sh
test -s paper/main.pdf

echo "All checks passed."
