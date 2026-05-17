#!/usr/bin/env python3
"""
Plot section-level Voynich lag spectra with null envelopes in a grid.

Input:
- CSV from section_lag_spectrum_compare.py

Output:
- section_spectra_grid.png
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot section-level lag spectra")
    parser.add_argument("--csv", default="artifacts/section_lag_spectrum_compare.csv", help="Long CSV from section_lag_spectrum_compare.py")
    parser.add_argument("--out", default="artifacts/plots/section_spectra_grid.png", help="Output PNG path")
    parser.add_argument("--target-lags", nargs="+", type=int, default=[5, 6, 12, 13], help="Lags to mark")
    parser.add_argument("--max-sections", type=int, default=16, help="Maximum section panels to render")
    return parser.parse_args()


def load_section_rows(path: str) -> dict[str, list[dict]]:
    by_section = defaultdict(list)
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("group") != "voynich_section":
                continue
            sec = row.get("section", "unknown")
            by_section[sec].append(
                {
                    "lag": int(row["lag"]),
                    "observed": float(row["observed"]),
                    "null_q025": float(row["null_q025"]),
                    "null_q975": float(row["null_q975"]),
                }
            )

    for sec in by_section:
        by_section[sec].sort(key=lambda x: x["lag"])
    return by_section


def render_grid(by_section: dict[str, list[dict]], out_path: str, target_lags: list[int], max_sections: int) -> bool:
    import matplotlib.pyplot as plt

    sections = sorted(by_section.keys())[:max_sections]
    if not sections:
        return False

    n = len(sections)
    cols = 3 if n > 4 else 2
    rows = int(math.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 3.2 * rows), squeeze=False)
    flat_axes = [ax for row in axes for ax in row]

    for i, section in enumerate(sections):
        ax = flat_axes[i]
        vals = by_section[section]
        lags = [v["lag"] for v in vals]
        obs = [v["observed"] for v in vals]
        ql = [v["null_q025"] for v in vals]
        qh = [v["null_q975"] for v in vals]

        ax.fill_between(lags, ql, qh, alpha=0.2, color="black")
        ax.plot(lags, obs, color="black", linewidth=1.8)
        for lag in target_lags:
            ax.axvline(lag, color="gray", linestyle=":", linewidth=0.7, alpha=0.8)
        ax.axhline(0.0, linestyle="--", linewidth=0.8, color="gray")
        ax.set_title(f"Section {section}")
        ax.set_xlabel("Lag")
        ax.set_ylabel("Autocorrelation deviation")

    for j in range(n, len(flat_axes)):
        flat_axes[j].axis("off")

    fig.suptitle("Voynich Section-Level Lag Spectra (Observed with Null 95% Bands)")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return True


def main() -> int:
    args = parse_args()

    rows = load_section_rows(args.csv)
    try:
        rendered = render_grid(rows, args.out, args.target_lags, args.max_sections)
    except ModuleNotFoundError as exc:
        print("ERROR: plotting requires matplotlib. Install with: pip install matplotlib")
        print(f"Missing module: {exc}")
        return 1

    if not rendered:
        print("No section-level rows found to plot.")
        print("Tip: lower --min-section-chars when generating section_lag_spectrum_compare output.")
        return 1

    print("=" * 80)
    print("SECTION SPECTRA GRID GENERATED")
    print("=" * 80)
    print(f"Output: {args.out}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
