# Covering the Unit Disk by 100 Equal Disks

This repository contains a LaTeX paper and reproducible verification code
for an explicit construction of 100 equal disks covering the unit disk.

The main certified statement is

\[
r_D(100)\le \frac{1}{\sqrt{67}}
=0.122169444356305223\ldots
\]

where \(r_D(N)\) is the least radius for which \(N\) equal disks can
cover the unit disk.

The paper also collects:

- the rigorous asymptotic theorem of Birgin, Gardenghi, and Laurain;
- its specialization to the unit disk;
- rigorous lower and constructive upper bounds for every \(N\le100\);
- an explicit finite certificate for the \(N=100\) construction.

The exact global value of \(r_D(100)\) is not known in the published
literature. This repository does not claim that the construction is
globally optimal.

## Build the paper

From the repository root:

```powershell
./scripts/build-paper.ps1
```

The compiled paper is written to `paper/main.pdf`.

Equivalently:

```powershell
Push-Location paper
Copy-Item references.bib ../dist/references.bib -Force
latexmk -pdf -outdir=../dist main.tex
Pop-Location
```

## Verify the certificate

```powershell
python scripts/verify_certificate.py
```

The script uses exact lattice indices and high-precision arithmetic. It
checks the finite number of elementary triangles meeting the target disk
and verifies that each has a selected lattice vertex.

## Regenerate the bounds table

```powershell
python scripts/generate_bounds.py
```

## Run all checks

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

## License

Code is released under the MIT License. Paper text and figures are
released under CC BY 4.0.
