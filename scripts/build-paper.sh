#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/dist"
cp "$ROOT/paper/references.bib" "$ROOT/dist/references.bib"

(
  cd "$ROOT/paper"
  latexmk -pdf -outdir="$ROOT/dist" main.tex
)

cp "$ROOT/dist/main.pdf" "$ROOT/paper/main.pdf"
