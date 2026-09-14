#!/usr/bin/env python3
"""Regenerate the N <= 100 bounds table.

The table combines:

* exact classical values for N <= 10;
* the known construction values for 11 <= N <= 25;
* the triangular-lattice shell construction for 26 <= N <= 100;
* the area lower bound and the BGL lower bound for N >= 10.
"""

from __future__ import annotations

import csv
from pathlib import Path

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
mp.mp.dps = 60

PI = mp.pi


def bgl_bounds(N: int):
    T = 3 * mp.sqrt(3) * N
    base = mp.sqrt(2 * PI / T)
    lower = (
        base
        - 4 * PI / T
        - 8 * PI * mp.sqrt(2 * PI) / T ** mp.mpf("1.5")
    )
    mu = (
        4 * PI + mp.sqrt(16 * PI**2 + 2 * PI * (T - 10 * PI))
    ) / (T - 16 * PI)
    upper = base + (4 * PI * mu + 8 * PI * mu**2) / mp.sqrt(2 * PI * T)
    return lower, upper


def lattice_table():
    """Compute the shell-construction upper bounds used in the paper.

    For the compact table in this repository, the exact radii obtained
    by the critical-ray calculation are recorded at shell boundaries.
    Values between shell boundaries use the last available construction.
    """
    # Values are supplied by verify_certificate.py / the paper's shell
    # calculation.  They are exact algebraic values where available.
    exact_upper = {
        19: 1 / mp.sqrt(13),
        37: mp.mpf(1) / 5,
        43: 1 / mp.sqrt(28),
        50: 1 / mp.sqrt(28),
        55: 1 / mp.sqrt(37),
        61: 1 / mp.sqrt(43),
        73: mp.mpf(1) / 7,
        80: mp.mpf(1) / 7,
        85: 1 / mp.sqrt(mp.mpf("61.01569036313012")),
        91: mp.mpf(1) / 8,
        97: 1 / mp.sqrt(67),
        100: 1 / mp.sqrt(67),
    }
    previous = mp.mpf(1)
    values = {}
    for N in range(1, 101):
        if N in exact_upper:
            previous = exact_upper[N]
        values[N] = previous
    return values


def main() -> None:
    DATA.mkdir(exist_ok=True)

    exact = {
        1: mp.mpf(1),
        2: mp.mpf(1),
        3: mp.sqrt(3) / 2,
        4: mp.sqrt(2) / 2,
        5: mp.mpf("0.60938286408070965467"),
        6: mp.mpf("0.555905211416588705"),
        7: mp.mpf(1) / 2,
        8: 1 / (1 + 2 * mp.cos(2 * PI / 7)),
        9: mp.sqrt(2) - 1,
        10: 1 / (1 + 2 * mp.cos(2 * PI / 9)),
    }

    known_upper = {
        11: 1 / mp.mpf("2.631"),
        12: 1 / mp.mpf("2.769"),
        13: 1 / mp.mpf("2.884791881779"),
        14: 1 / mp.mpf("3.014481257988"),
        15: 1 / mp.mpf("3.143241301320"),
        16: 1 / mp.mpf("3.244437877904"),
        17: 1 / mp.mpf("3.349729261451"),
        18: 1 / mp.mpf("3.446282750304"),
        19: 1 / mp.mpf("3.605551275463"),
        20: 1 / mp.mpf("3.692105318041"),
        21: 1 / mp.mpf("3.804522530536"),
        22: 1 / mp.mpf("3.948644563198"),
        23: 1 / mp.mpf("4.000739711391"),
        24: 1 / mp.mpf("4.076613423974"),
        25: 1 / mp.mpf("4.181540550352"),
    }

    lattice = lattice_table()
    rows = []
    for N in range(1, 101):
        if N <= 10:
            lo = hi = exact[N]
            status = "proved exact"
        else:
            bgl_lower, bgl_upper = bgl_bounds(N)
            lo = max(mp.mpf(1) / mp.sqrt(N), bgl_lower)
            if N <= 25:
                hi = known_upper[N]
                status = "known construction upper"
            else:
                hi = min(lattice[N], bgl_upper)
                status = "lattice construction upper"
        if lo > hi:
            raise AssertionError(f"invalid interval at N={N}: {lo} > {hi}")
        rows.append(
            {
                "N": N,
                "lower_bound": mp.nstr(lo, 25),
                "upper_bound": mp.nstr(hi, 25),
                "status": status,
            }
        )

    with (DATA / "r_D_N1-100_bounds.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["N", "lower_bound", "upper_bound", "status"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {DATA / 'r_D_N1-100_bounds.csv'}")


if __name__ == "__main__":
    main()
