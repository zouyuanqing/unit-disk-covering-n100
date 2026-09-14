$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    python scripts/verify_certificate.py
    if ($LASTEXITCODE -ne 0) { throw "certificate verification failed" }

    python scripts/generate_bounds.py
    if ($LASTEXITCODE -ne 0) { throw "bounds generation failed" }

    & (Join-Path $PSScriptRoot "build-paper.ps1")
    if ($LASTEXITCODE -ne 0) { throw "paper build failed" }

    if (-not (Test-Path "paper/main.pdf")) {
        throw "paper/main.pdf was not produced"
    }
    Write-Host "All checks passed."
}
finally {
    Pop-Location
}
