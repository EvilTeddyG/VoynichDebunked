#!/usr/bin/env python3
"""
Quantify preprocessing sensitivity for periodicity targets.

Builds a variant matrix over tokenization/normalization strategies and reports
how target lags move under shuffled-null calibration.

Outputs:
- CSV matrix of target-lag metrics by variant.
- JSON summary with rank/z/p dispersion by lag.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter
from statistics import mean

from corpus_provenance import ensure_publication_inputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocessing sensitivity matrix for periodicity targets")
    parser.add_argument("--input", default="data/takahashi_eva.txt", help="Transcript path")
    parser.add_argument("--target-lags", nargs="+", type=int, default=[5, 6, 12, 13], help="Target lags")
    parser.add_argument("--max-char-lag", type=int, default=60, help="Maximum lag")
    parser.add_argument("--permutations", type=int, default=300, help="Null permutations")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument(
        "--allow-placeholder-inputs",
        action="store_true",
        help="Allow synthetic/demo transcript inputs instead of publication-grade corpora",
    )
    parser.add_argument("--csv-out", default="artifacts/preprocessing_sensitivity.csv", help="Output CSV")
    parser.add_argument("--json-out", default="artifacts/preprocessing_sensitivity.json", help="Output JSON")
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


def rank_lag(profile: dict[int, float], lag: int) -> int:
    ranked = sorted(profile.items(), key=lambda kv: kv[1], reverse=True)
    for i, (k, _) in enumerate(ranked, start=1):
        if k == lag:
            return i
    return len(ranked) + 1


def lag_profile(chars: list[str], max_lag: int) -> dict[int, float]:
    n = len(chars)
    if n == 0:
        return {lag: 0.0 for lag in range(1, max_lag + 1)}

    probs = Counter(chars)
    expected = sum((v / n) ** 2 for v in probs.values())

    out = {}
    for lag in range(1, max_lag + 1):
        if lag >= n:
            out[lag] = 0.0
            continue
        comp = n - lag
        matches = 0
        for i in range(comp):
            if chars[i] == chars[i + lag]:
                matches += 1
        observed = matches / comp if comp else 0.0
        out[lag] = observed - expected
    return out


def load_voynich_lines(path: str) -> list[str]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            if not raw.startswith("<f"):
                continue
            parts = raw.split(">", 1)
            if len(parts) < 2:
                continue
            out.append(parts[1].strip())
    return out


def tokenize_variant(lines: list[str], variant: str) -> list[str]:
    if variant == "alpha_split":
        tokens = []
        for line in lines:
            toks = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in re.split(r"[\s.-]", line)]
            tokens.extend([w for w in toks if w])
        return tokens

    if variant == "alpha_keep_dots":
        tokens = []
        for line in lines:
            toks = [re.sub(r"[^a-zA-Z.]", "", w).strip(".") for w in re.split(r"[\s-]", line)]
            tokens.extend([w for w in toks if w])
        return tokens

    if variant == "alpha_collapse_runs":
        tokens = []
        for line in lines:
            toks = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in re.split(r"[\s.-]", line)]
            toks = [re.sub(r"(.)\1+", r"\1", w) for w in toks if w]
            tokens.extend([w for w in toks if w])
        return tokens

    if variant == "alpha_min_len_2":
        tokens = []
        for line in lines:
            toks = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in re.split(r"[\s.-]", line)]
            tokens.extend([w for w in toks if len(w) >= 2])
        return tokens

    raise ValueError(f"Unknown variant: {variant}")


def chars_from_tokens(tokens: list[str]) -> list[str]:
    return [c for w in tokens for c in w if c.isalpha()]


def evaluate_variant(chars: list[str], max_lag: int, target_lags: list[int], permutations: int) -> tuple[dict, dict[str, dict[str, float]]]:
    obs = lag_profile(chars, max_lag)
    null_by_lag = {lag: [] for lag in range(1, max_lag + 1)}

    for _ in range(permutations):
        s = chars[:]
        random.shuffle(s)
        prof = lag_profile(s, max_lag)
        for lag, v in prof.items():
            null_by_lag[lag].append(v)

    metrics = {
        "char_count": len(chars),
        "peak_lag": max(obs, key=lambda k: obs[k]) if obs else None,
        "peak_value": max(obs.values()) if obs else 0.0,
    }

    targets: dict[str, dict[str, float]] = {}
    for lag in target_lags:
        vals = null_by_lag.get(lag, [])
        vals_sorted = sorted(vals)
        nm = mean(vals) if vals else 0.0
        ns = stddev(vals)
        ov = obs.get(lag, 0.0)
        p = (sum(1 for x in vals if x >= ov) + 1) / (len(vals) + 1) if vals else 1.0
        z = (ov - nm) / ns if ns > 0 else 0.0
        targets[str(lag)] = {
            "observed": ov,
            "null_mean": nm,
            "null_sd": ns,
            "null_q025": percentile(vals_sorted, 2.5),
            "null_q975": percentile(vals_sorted, 97.5),
            "p_value_ge": p,
            "z_score": z,
            "rank": rank_lag(obs, lag),
        }

    return metrics, targets


def summarize_dispersion(variants: dict[str, dict], target_lags: list[int]) -> dict[str, dict[str, float]]:
    out = {}
    for lag in target_lags:
        key = str(lag)
        z_vals = [variants[v]["targets"][key]["z_score"] for v in variants]
        p_vals = [variants[v]["targets"][key]["p_value_ge"] for v in variants]
        rank_vals = [variants[v]["targets"][key]["rank"] for v in variants]
        out[key] = {
            "z_min": min(z_vals),
            "z_max": max(z_vals),
            "z_range": max(z_vals) - min(z_vals),
            "p_min": min(p_vals),
            "p_max": max(p_vals),
            "rank_min": min(rank_vals),
            "rank_max": max(rank_vals),
        }
    return out


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    ensure_publication_inputs(
        voynich_path=args.input,
        allow_placeholder_inputs=args.allow_placeholder_inputs,
    )

    lines = load_voynich_lines(args.input)
    if not lines:
        print("ERROR: no Voynich lines parsed; expected <f...> tagged lines")
        return 1

    variant_names = [
        "alpha_split",
        "alpha_keep_dots",
        "alpha_collapse_runs",
        "alpha_min_len_2",
    ]

    results = {
        "input_file": args.input,
        "seed": args.seed,
        "permutations": args.permutations,
        "target_lags": args.target_lags,
        "max_char_lag": args.max_char_lag,
        "variants": {},
    }

    rows = []
    for name in variant_names:
        toks = tokenize_variant(lines, name)
        chars = chars_from_tokens(toks)
        metrics, targets = evaluate_variant(chars, args.max_char_lag, args.target_lags, args.permutations)
        results["variants"][name] = {
            "counts": {"tokens": len(toks), "chars": len(chars)},
            "metrics": metrics,
            "targets": targets,
        }
        for lag_key, vals in targets.items():
            rows.append(
                {
                    "variant": name,
                    "target_lag": int(lag_key),
                    "tokens": len(toks),
                    "chars": len(chars),
                    "peak_lag": metrics["peak_lag"],
                    "peak_value": metrics["peak_value"],
                    **vals,
                }
            )

    results["dispersion_by_lag"] = summarize_dispersion(results["variants"], args.target_lags)

    with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "variant",
            "target_lag",
            "tokens",
            "chars",
            "peak_lag",
            "peak_value",
            "observed",
            "null_mean",
            "null_sd",
            "null_q025",
            "null_q975",
            "p_value_ge",
            "z_score",
            "rank",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("PREPROCESSING SENSITIVITY COMPLETE")
    print("=" * 80)
    print(f"Variants: {len(variant_names)}")
    print(f"CSV: {args.csv_out}")
    print(f"JSON: {args.json_out}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
