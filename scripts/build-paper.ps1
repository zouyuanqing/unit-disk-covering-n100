$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root "dist"
New-Item -ItemType Directory -Force -Path $out | Out-Null
Copy-Item (Join-Path $root "paper/references.bib") (Join-Path $out "references.bib") -Force

Push-Location (Join-Path $root "paper")
try {
    latexmk -pdf -outdir="$out" "main.tex"
}
finally {
    Pop-Location
}

Copy-Item (Join-Path $out "main.pdf") (Join-Path $root "paper/main.pdf") -Force
