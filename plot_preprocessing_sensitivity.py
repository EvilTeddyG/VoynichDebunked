#!/usr/bin/env python3
"""
Plot preprocessing sensitivity heatmaps for z-scores and p-values by lag/variant.
"""

from __future__ import annotations

import argparse
import csv
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot preprocessing sensitivity heatmap")
    parser.add_argument("--csv", default="artifacts/preprocessing_sensitivity.csv", help="CSV from preprocessing_sensitivity.py")
    parser.add_argument("--out", default="artifacts/plots/preprocessing_sensitivity_heatmap.png", help="Output image path")
    return parser.parse_args()


def load_rows(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "variant": row["variant"],
                    "target_lag": int(row["target_lag"]),
                    "z_score": float(row["z_score"]),
                    "p_value_ge": float(row["p_value_ge"]),
                }
            )
    return rows


def matrix(rows: list[dict], value_key: str):
    variants = sorted({r["variant"] for r in rows})
    lags = sorted({r["target_lag"] for r in rows})
    arr = []
    for v in variants:
        vals = []
        for lag in lags:
            cell = next((r for r in rows if r["variant"] == v and r["target_lag"] == lag), None)
            vals.append(cell[value_key] if cell else 0.0)
        arr.append(vals)
    return variants, lags, arr


def annotate(ax, arr, fmt: str = "{:.2f}"):
    for i, row in enumerate(arr):
        for j, val in enumerate(row):
            ax.text(j, i, fmt.format(val), ha="center", va="center", fontsize=8)


def main() -> int:
    args = parse_args()
    rows = load_rows(args.csv)
    if not rows:
        print("ERROR: no rows in preprocessing sensitivity CSV")
        return 1

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        print("ERROR: plotting requires matplotlib. Install with: pip install matplotlib")
        print(f"Missing module: {exc}")
        return 1

    variants, lags, z_arr = matrix(rows, "z_score")
    _, _, p_arr = matrix(rows, "p_value_ge")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    im1 = ax1.imshow(z_arr, aspect="auto", cmap="coolwarm")
    ax1.set_title("Preprocessing Sensitivity: z-score")
    ax1.set_xlabel("Target lag")
    ax1.set_ylabel("Variant")
    ax1.set_xticks(range(len(lags)), labels=[str(l) for l in lags])
    ax1.set_yticks(range(len(variants)), labels=variants)
    annotate(ax1, z_arr, fmt="{:+.2f}")
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    im2 = ax2.imshow(p_arr, aspect="auto", cmap="viridis_r", vmin=0.0, vmax=1.0)
    ax2.set_title("Preprocessing Sensitivity: p-value (null >= observed)")
    ax2.set_xlabel("Target lag")
    ax2.set_ylabel("Variant")
    ax2.set_xticks(range(len(lags)), labels=[str(l) for l in lags])
    ax2.set_yticks(range(len(variants)), labels=variants)
    annotate(ax2, p_arr, fmt="{:.3f}")
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    fig.suptitle("Lag-Target Stability Under Preprocessing Variants")
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fig.savefig(args.out, dpi=180)
    plt.close(fig)

    print("=" * 80)
    print("PREPROCESSING HEATMAP GENERATED")
    print("=" * 80)
    print(f"Output: {args.out}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
