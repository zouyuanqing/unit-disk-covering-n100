#!/usr/bin/env python3
"""Finite certificate for the N=100 disk-covering construction.

The script verifies two finite assertions:

1. Every elementary triangular-lattice triangle that meets the disk of
   radius sqrt(67) has at least one vertex in the 97-point set A.
2. Along the critical ray through
       p = (-7*sqrt(3)/2, -11/2),
   the union of the radial intervals has maximal endpoint sqrt(67).

The computations use mpmath at 80 decimal digits.  The resulting
certificate files are written under data/.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
mp.mp.dps = 80

SQRT3 = mp.sqrt(3)
SQRT67 = mp.sqrt(67)

# Triangular-lattice basis of edge length sqrt(3).
U = (SQRT3, mp.mpf(0))
V = (SQRT3 / 2, mp.mpf(3) / 2)


def center(ij: tuple[int, int]) -> tuple[mp.mpf, mp.mpf]:
    i, j = ij
    return (
        mp.mpf(i) * U[0] + mp.mpf(j) * V[0],
        mp.mpf(i) * U[1] + mp.mpf(j) * V[1],
    )


def qform(ij: tuple[int, int]) -> int:
    i, j = ij
    return i * i + i * j + j * j


def distance_sq(a: tuple[mp.mpf, mp.mpf], b: tuple[mp.mpf, mp.mpf]) -> mp.mpf:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def point_triangle_distance_sq(
    a: tuple[mp.mpf, mp.mpf],
    b: tuple[mp.mpf, mp.mpf],
    c: tuple[mp.mpf, mp.mpf],
) -> mp.mpf:
    """Squared distance from the origin to the closed triangle abc."""
    zero = (mp.mpf(0), mp.mpf(0))

    def cross(x, y):
        return x[0] * y[1] - x[1] * y[0]

    def sub(x, y):
        return (x[0] - y[0], x[1] - y[1])

    def same_side(p, q, r, s):
        return cross(sub(s, r), sub(p, r)) * cross(sub(s, r), sub(q, r)) >= 0

    if (
        same_side(zero, a, b, c)
        and same_side(zero, b, a, c)
        and same_side(zero, c, a, b)
    ):
        return mp.mpf(0)

    best = mp.inf
    for x, y in ((a, b), (b, c), (c, a)):
        ex, ey = y[0] - x[0], y[1] - x[1]
        denom = ex * ex + ey * ey
        t = -(x[0] * ex + x[1] * ey) / denom
        t = max(mp.mpf(0), min(mp.mpf(1), t))
        px, py = x[0] + t * ex, x[1] + t * ey
        best = min(best, px * px + py * py)
    return best


def main() -> None:
    DATA.mkdir(exist_ok=True)

    A = [
        (i, j)
        for i in range(-12, 13)
        for j in range(-12, 13)
        if qform((i, j)) <= 27
    ]
    if len(A) != 97:
        raise AssertionError(f"expected 97 points in A, got {len(A)}")

    # Any triangle meeting D_sqrt67 has all vertices within
    # R + sqrt(3) < R + 2.
    pool = []
    for i in range(-12, 13):
        for j in range(-12, 13):
            p = center((i, j))
            if p[0] * p[0] + p[1] * p[1] <= (SQRT67 + 2) ** 2:
                pool.append((i, j))

    index = {ij: k for k, ij in enumerate(pool)}
    coords = [center(ij) for ij in pool]

    neighbors: dict[int, set[int]] = {k: set() for k in range(len(pool))}
    target_edge_sq = 3
    for k in range(len(pool)):
        for l in range(k + 1, len(pool)):
            if abs(distance_sq(coords[k], coords[l]) - target_edge_sq) < mp.mpf("1e-60"):
                neighbors[k].add(l)
                neighbors[l].add(k)

    triangles = set()
    for a in range(len(pool)):
        for b in neighbors[a]:
            if b <= a:
                continue
            for c in neighbors[a].intersection(neighbors[b]):
                if c <= b:
                    continue
                triangle = tuple(sorted((a, b, c)))
                d2 = point_triangle_distance_sq(
                    coords[a], coords[b], coords[c]
                )
                if d2 <= 67:
                    triangles.add(triangle)

    rows = []
    all_outside = []
    boundary = []
    for triangle in sorted(triangles):
        ij = [pool[k] for k in triangle]
        flags = [x in A for x in ij]
        selected = [x for x, flag in zip(ij, flags) if flag]
        if not selected:
            all_outside.append(ij)
        if len(selected) == 1:
            boundary.append((ij, selected[0]))
        rows.append(
            {
                "v1_i": ij[0][0],
                "v1_j": ij[0][1],
                "v2_i": ij[1][0],
                "v2_j": ij[1][1],
                "v3_i": ij[2][0],
                "v3_j": ij[2][1],
                "selected_i": selected[0][0] if selected else "",
                "selected_j": selected[0][1] if selected else "",
                "vertices_in_A": sum(flags),
            }
        )

    if all_outside:
        raise AssertionError(f"found {len(all_outside)} uncovered triangles")

    with (DATA / "delaunay_triangles.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "v1_i",
                "v1_j",
                "v2_i",
                "v2_j",
                "v3_i",
                "v3_j",
                "selected_i",
                "selected_j",
                "vertices_in_A",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    # Critical-ray certificate.
    p = (-mp.mpf(7) * SQRT3 / 2, -mp.mpf(11) / 2)
    norm_p = mp.sqrt(p[0] * p[0] + p[1] * p[1])
    if abs(norm_p - SQRT67) > mp.mpf("1e-60"):
        raise AssertionError("critical point does not have norm sqrt(67)")
    e = (p[0] / norm_p, p[1] / norm_p)

    intervals = []
    for ij in A:
        c = center(ij)
        proj = c[0] * e[0] + c[1] * e[1]
        perp_sq = c[0] * c[0] + c[1] * c[1] - proj * proj
        if perp_sq <= 1:
            h = mp.sqrt(max(mp.mpf(0), 1 - perp_sq))
            intervals.append((proj - h, proj + h, ij))

    intervals.sort()
    merged = []
    for lo, hi, ij in intervals:
        if not merged or lo > merged[-1][1] + mp.mpf("1e-60"):
            merged.append([lo, hi, [ij]])
        else:
            if hi > merged[-1][1]:
                merged[-1][1] = hi
            merged[-1][2].append(ij)

    max_endpoint = max(hi for _, hi, _ in merged)
    if abs(max_endpoint - SQRT67) > mp.mpf("1e-50"):
        raise AssertionError(
            f"critical ray endpoint {mp.nstr(max_endpoint, 30)} "
            f"is not sqrt(67)"
        )

    interval_rows = []
    for lo, hi, ij in intervals:
        interval_rows.append(
            {
                "center_i": ij[0],
                "center_j": ij[1],
                "left_endpoint": mp.nstr(lo, 50),
                "right_endpoint": mp.nstr(hi, 50),
            }
        )
    with (DATA / "critical_ray_intervals.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "center_i",
                "center_j",
                "left_endpoint",
                "right_endpoint",
            ],
        )
        writer.writeheader()
        writer.writerows(interval_rows)

    summary = {
        "points_in_A": len(A),
        "lattice_points_in_pool": len(pool),
        "triangles_meeting_target_disk": len(triangles),
        "triangles_with_three_A_vertices": sum(
            1 for row in rows if row["vertices_in_A"] == 3
        ),
        "triangles_with_two_A_vertices": sum(
            1 for row in rows if row["vertices_in_A"] == 2
        ),
        "triangles_with_one_A_vertex": sum(
            1 for row in rows if row["vertices_in_A"] == 1
        ),
        "triangles_with_no_A_vertex": sum(
            1 for row in rows if row["vertices_in_A"] == 0
        ),
        "critical_ray_max_endpoint": mp.nstr(max_endpoint, 60),
        "critical_point": [mp.nstr(p[0], 50), mp.nstr(p[1], 50)],
        "target_squared_radius": 67,
    }
    with (DATA / "certificate_summary.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    print("Certificate verified.")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
