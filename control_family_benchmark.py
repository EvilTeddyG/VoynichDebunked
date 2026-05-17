#!/usr/bin/env python3
"""
Control-family benchmark for Voynich hypothesis testing.

This script compares Voynich metrics against *labeled control families*
(e.g., liturgical repetition, alchemical notation, glossolalia, ornamental
pseudo-script, recipe corpora), then reports class-conditional effect sizes.

Expected manifest CSV columns:
  label,path,family,notes
Where:
  - label: short corpus id
  - path: relative or absolute file path
  - family: comparison family name
  - notes: optional free text

Text format assumptions:
  - Voynich file uses Takahashi-style lines beginning with <f...>
  - Control corpora are plain text (one logical line per line)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from statistics import mean


DEFAULT_LAGS = [5, 6, 12, 13]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Class-aware control benchmark")
    parser.add_argument("--voynich", default="data/takahashi_eva.txt", help="Voynich transcript path")
    parser.add_argument(
        "--manifest",
        default="data/baselines/manifest_template.csv",
        help="Control manifest CSV path",
    )
    parser.add_argument("--lags", nargs="+", type=int, default=DEFAULT_LAGS, help="Lag metrics")
    parser.add_argument("--min-word-count", type=int, default=20, help="Min token count for polarization")
    parser.add_argument(
        "--csv-out",
        default="artifacts/control_family_benchmark.csv",
        help="Output CSV summary",
    )
    parser.add_argument(
        "--json-out",
        default="artifacts/control_family_benchmark.json",
        help="Output JSON detail",
    )
    return parser.parse_args()


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = max(0, min(len(sorted_vals) - 1, int(round((p / 100.0) * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def stddev(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))


def load_manifest(path: str) -> list[dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"label", "path", "family"}
        if not required.issubset(set(r.fieldnames or [])):
            raise ValueError("Manifest must include columns: label,path,family")
        for row in r:
            if not row.get("label") or not row.get("path") or not row.get("family"):
                continue
            rows.append(row)
    return rows


def resolve_path(base_manifest: str, rel_or_abs: str) -> str:
    if os.path.isabs(rel_or_abs):
        return rel_or_abs
    return os.path.normpath(os.path.join(os.path.dirname(base_manifest), rel_or_abs))


def extract_lines(path: str, voynich_mode: bool) -> list[str]:
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            if voynich_mode:
                if not raw.startswith("<f"):
                    continue
                parts = raw.split(">", 1)
                if len(parts) < 2:
                    continue
                raw = parts[1]
            lines.append(raw.strip())
    return lines


def normalize_words(line: str) -> list[str]:
    words = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in re.split(r"[\s.-]", line)]
    return [w for w in words if w]


def entropy_h0_h1(chars: list[str]) -> tuple[float, float]:
    if not chars:
        return 0.0, 0.0

    n = len(chars)
    counts = Counter(chars)
    h0 = 0.0
    for c in counts.values():
        p = c / n
        h0 -= p * math.log2(p)

    if n < 2:
        return h0, 0.0

    bi = Counter((chars[i], chars[i + 1]) for i in range(n - 1))
    left = Counter(chars[i] for i in range(n - 1))
    h1 = 0.0
    for (c1, c2), k in bi.items():
        p_bigram = k / (n - 1)
        p_cond = k / left[c1]
        h1 -= p_bigram * math.log2(p_cond)
    return h1 + (h0 - h1), h1


def mean_max_polarization(lines_words: list[list[str]], min_word_count: int) -> float:
    pos = defaultdict(Counter)
    totals = Counter()

    for words in lines_words:
        if len(words) < 3:
            continue
        pos["start"][words[0]] += 1
        pos["end"][words[-1]] += 1
        for w in words[1:-1]:
            pos["mid"][w] += 1
        for w in words:
            totals[w] += 1

    vals = []
    for w, total in totals.items():
        if total < min_word_count:
            continue
        p_start = pos["start"][w] / total
        p_mid = pos["mid"][w] / total
        p_end = pos["end"][w] / total
        vals.append(max(p_start, p_mid, p_end))
    return mean(vals) if vals else 0.0


def autocorr_score(chars: list[str], lag: int) -> float:
    if lag <= 0 or lag >= len(chars):
        return 0.0
    counts = Counter(chars)
    n = len(chars)
    expected = sum((v / n) ** 2 for v in counts.values())
    m = n - lag
    matches = 0
    for i in range(m):
        if chars[i] == chars[i + lag]:
            matches += 1
    observed = matches / m if m else 0.0
    return observed - expected


def metric_vector(record: dict, lags: list[int]) -> list[float]:
    vec = [record["H1"], record["mean_max_polarization"]]
    vec.extend(record[f"lag_{lag}"] for lag in lags)
    return vec


def l2(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def compute_metrics(path: str, voynich_mode: bool, lags: list[int], min_word_count: int) -> dict:
    raw_lines = extract_lines(path, voynich_mode)
    lines_words = [normalize_words(line) for line in raw_lines]
    words = [w for line in lines_words for w in line]
    chars = [c for w in words for c in w if c.isalpha()]

    h0, h1 = entropy_h0_h1(chars)
    pol = mean_max_polarization(lines_words, min_word_count)

    out = {
        "tokens": len(words),
        "chars": len(chars),
        "H0": h0,
        "H1": h1,
        "mean_max_polarization": pol,
    }
    for lag in lags:
        out[f"lag_{lag}"] = autocorr_score(chars, lag)
    return out


def class_effect_sizes(voynich_row: dict, control_rows: list[dict], lags: list[int]) -> list[dict]:
    grouped = defaultdict(list)
    for row in control_rows:
        grouped[row["family"]].append(row)

    out = []
    for family, rows in grouped.items():
        family_stats = {"family": family, "n": len(rows)}
        for key in ["H1", "mean_max_polarization"] + [f"lag_{lag}" for lag in lags]:
            vals = [r[key] for r in rows]
            m = mean(vals) if vals else 0.0
            sd = stddev(vals)
            z = ((voynich_row[key] - m) / sd) if sd > 0 else 0.0
            family_stats[f"{key}_mean"] = m
            family_stats[f"{key}_sd"] = sd
            family_stats[f"{key}_z"] = z
            family_stats[f"{key}_q025"] = percentile(sorted(vals), 2.5)
            family_stats[f"{key}_q975"] = percentile(sorted(vals), 97.5)
        out.append(family_stats)
    return sorted(out, key=lambda r: r["family"])


def main() -> int:
    args = parse_args()

    manifest_rows = load_manifest(args.manifest)

    voynich_metrics = compute_metrics(args.voynich, True, args.lags, args.min_word_count)
    voynich_row = {
        "label": "voynich",
        "path": args.voynich,
        "family": "voynich",
        **voynich_metrics,
    }

    controls = []
    for mrow in manifest_rows:
        fpath = resolve_path(args.manifest, mrow["path"])
        if not os.path.exists(fpath):
            continue
        metrics = compute_metrics(fpath, False, args.lags, args.min_word_count)
        controls.append(
            {
                "label": mrow["label"],
                "path": fpath,
                "family": mrow["family"],
                "notes": mrow.get("notes", ""),
                **metrics,
            }
        )

    if not controls:
        print("ERROR: no control corpora resolved from manifest")
        return 1

    # Distance to each control and nearest-family summary
    vvec = metric_vector(voynich_row, args.lags)
    for crow in controls:
        crow["distance_to_voynich"] = l2(vvec, metric_vector(crow, args.lags))

    nearest_controls = sorted(controls, key=lambda r: r["distance_to_voynich"])[:10]

    family_effects = class_effect_sizes(voynich_row, controls, args.lags)

    # Output tabular summary CSV
    os.makedirs(os.path.dirname(args.csv_out), exist_ok=True)
    summary_rows = [voynich_row] + controls
    fieldnames = list(summary_rows[0].keys())
    with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(summary_rows)

    report = {
        "voynich": voynich_row,
        "controls": controls,
        "nearest_controls": nearest_controls,
        "family_effect_sizes": family_effects,
        "lags": args.lags,
        "manifest": args.manifest,
    }

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=" * 80)
    print("CONTROL-FAMILY BENCHMARK COMPLETE")
    print("=" * 80)
    print(f"Manifest: {args.manifest}")
    print(f"Controls loaded: {len(controls)}")
    print(f"CSV summary: {args.csv_out}")
    print(f"JSON detail: {args.json_out}")
    print("Top nearest controls:")
    for row in nearest_controls:
        print(f"  - {row['label']} ({row['family']}): distance={row['distance_to_voynich']:.6f}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
