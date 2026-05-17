#!/usr/bin/env python3
"""
Periodicity robustness audit for Voynich-style corpora.

Purpose:
- Stress-test periodicity claims (word-distance peaks, lag peaks) across
  normalization/tokenization variants.
- Estimate false-positive behavior under shuffled null corpora.

Outputs:
- Per-variant observed metrics.
- Null distribution summaries.
- Empirical p-values and z-scores for target periodicities.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter, defaultdict
from statistics import mean

from corpus_provenance import ensure_publication_inputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robustness audit for periodicity claims")
    parser.add_argument("--input", default="data/takahashi_eva.txt", help="Transcript file path")
    parser.add_argument("--target-word-distance", type=int, default=13, help="Target word-distance peak")
    parser.add_argument("--target-char-lags", nargs="+", type=int, default=[5, 6], help="Target char lags")
    parser.add_argument("--max-word-lag", type=int, default=40, help="Maximum word lag for repetition profile")
    parser.add_argument("--max-char-lag", type=int, default=60, help="Maximum char lag for autocorrelation")
    parser.add_argument("--permutations", type=int, default=400, help="Null permutations per variant")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument(
        "--allow-placeholder-inputs",
        action="store_true",
        help="Allow synthetic/demo transcript inputs instead of publication-grade corpora",
    )
    parser.add_argument("--json-out", default="artifacts/periodicity_robustness.json", help="Output JSON path")
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
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def read_takahashi_lines(path: str) -> list[str]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("<f"):
                continue
            parts = line.split(">", 1)
            if len(parts) < 2:
                continue
            out.append(parts[1].strip())
    return out


def words_variant(line: str, variant: str) -> list[str]:
    if variant == "alpha_split":
        # Keep only letters; split on whitespace, hyphen, and period.
        raw = re.split(r"[\s.-]", line)
        words = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in raw]
        return [w for w in words if w]

    if variant == "alpha_keep_dots":
        # Keep periods in-token (more conservative against over-splitting).
        raw = re.split(r"\s+", line)
        words = [re.sub(r"[^a-zA-Z.]", "", w).strip(".") for w in raw]
        return [w for w in words if w]

    if variant == "alpha_collapse_runs":
        # Collapse repeated letters to test sensitivity to glyph-run normalization.
        raw = re.split(r"[\s.-]", line)
        words = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in raw]
        words = [re.sub(r"(.)\1+", r"\1", w) for w in words if w]
        return [w for w in words if w]

    if variant == "alpha_min_len_2":
        raw = re.split(r"[\s.-]", line)
        words = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in raw]
        return [w for w in words if len(w) >= 2]

    raise ValueError(f"Unknown variant: {variant}")


def build_tokens(lines: list[str], variant: str) -> list[str]:
    tokens: list[str] = []
    for line in lines:
        tokens.extend(words_variant(line, variant))
    return tokens


def char_stream(words: list[str]) -> list[str]:
    return [c for w in words for c in w if c.isalpha()]


def word_lag_repetition_profile(words: list[str], max_lag: int) -> dict[int, float]:
    # Repetition rate at lag k: P(word_i == word_{i+k}).
    profile: dict[int, float] = {}
    n = len(words)
    for lag in range(1, max_lag + 1):
        if lag >= n:
            profile[lag] = 0.0
            continue
        m = n - lag
        matches = 0
        for i in range(m):
            if words[i] == words[i + lag]:
                matches += 1
        profile[lag] = matches / m if m else 0.0
    return profile


def char_autocorr_profile(chars: list[str], max_lag: int) -> dict[int, float]:
    n = len(chars)
    if n == 0:
        return {k: 0.0 for k in range(1, max_lag + 1)}
    probs = Counter(chars)
    expected = sum((v / n) ** 2 for v in probs.values())

    out: dict[int, float] = {}
    for lag in range(1, max_lag + 1):
        if lag >= n:
            out[lag] = 0.0
            continue
        m = n - lag
        matches = 0
        for i in range(m):
            if chars[i] == chars[i + lag]:
                matches += 1
        observed = matches / m if m else 0.0
        out[lag] = observed - expected
    return out


def top_peak(profile: dict[int, float]) -> tuple[int, float]:
    if not profile:
        return 0, 0.0
    lag = max(profile, key=lambda k: profile[k])
    return lag, profile[lag]


def rank_of_lag(profile: dict[int, float], lag: int) -> int:
    ordered = sorted(profile.items(), key=lambda kv: kv[1], reverse=True)
    for i, (k, _) in enumerate(ordered, start=1):
        if k == lag:
            return i
    return len(ordered) + 1


def evaluate_variant(
    words: list[str],
    target_word_distance: int,
    target_char_lags: list[int],
    max_word_lag: int,
    max_char_lag: int,
    permutations: int,
) -> dict:
    chars = char_stream(words)

    w_profile = word_lag_repetition_profile(words, max_word_lag)
    c_profile = char_autocorr_profile(chars, max_char_lag)

    w_peak_lag, w_peak_val = top_peak(w_profile)
    c_peak_lag, c_peak_val = top_peak(c_profile)

    obs_w = w_profile.get(target_word_distance, 0.0)
    obs_c = {lag: c_profile.get(lag, 0.0) for lag in target_char_lags}

    # Nulls
    null_w = []
    null_w_max = []
    null_c: dict[int, list[float]] = {lag: [] for lag in target_char_lags}
    null_c_max = []

    for _ in range(permutations):
        w_perm = words[:]
        random.shuffle(w_perm)
        wp = word_lag_repetition_profile(w_perm, max_word_lag)
        null_w.append(wp.get(target_word_distance, 0.0))
        null_w_max.append(max(wp.values()) if wp else 0.0)

        c_perm = chars[:]
        random.shuffle(c_perm)
        cp = char_autocorr_profile(c_perm, max_char_lag)
        for lag in target_char_lags:
            null_c[lag].append(cp.get(lag, 0.0))
        null_c_max.append(max(cp.values()) if cp else 0.0)

    # Stats
    null_w_sorted = sorted(null_w)
    null_w_mean = mean(null_w) if null_w else 0.0
    null_w_sd = stddev(null_w)
    p_w = (sum(1 for x in null_w if x >= obs_w) + 1) / (len(null_w) + 1)
    z_w = (obs_w - null_w_mean) / null_w_sd if null_w_sd > 0 else 0.0

    char_stats = {}
    for lag in target_char_lags:
        vals = null_c[lag]
        s_mean = mean(vals) if vals else 0.0
        s_sd = stddev(vals)
        obs = obs_c[lag]
        p = (sum(1 for x in vals if x >= obs) + 1) / (len(vals) + 1)
        z = (obs - s_mean) / s_sd if s_sd > 0 else 0.0
        vals_sorted = sorted(vals)
        char_stats[str(lag)] = {
            "observed": obs,
            "null_mean": s_mean,
            "null_sd": s_sd,
            "null_q025": percentile(vals_sorted, 2.5),
            "null_q975": percentile(vals_sorted, 97.5),
            "p_value_ge": p,
            "z_score": z,
            "rank_in_char_profile": rank_of_lag(c_profile, lag),
        }

    # False-positive framing: how often shuffled max-peak exceeds observed target score
    fp_word = (sum(1 for x in null_w_max if x >= obs_w) + 1) / (len(null_w_max) + 1)
    fp_char = {
        str(lag): (sum(1 for x in null_c_max if x >= obs_c[lag]) + 1) / (len(null_c_max) + 1)
        for lag in target_char_lags
    }

    return {
        "counts": {"tokens": len(words), "chars": len(chars)},
        "word_profile": {
            "target_distance": target_word_distance,
            "target_observed": obs_w,
            "target_rank": rank_of_lag(w_profile, target_word_distance),
            "peak_lag": w_peak_lag,
            "peak_value": w_peak_val,
            "null_mean": null_w_mean,
            "null_sd": null_w_sd,
            "null_q025": percentile(null_w_sorted, 2.5),
            "null_q975": percentile(null_w_sorted, 97.5),
            "p_value_ge": p_w,
            "z_score": z_w,
            "false_positive_rate_vs_null_max": fp_word,
        },
        "char_profile": {
            "peak_lag": c_peak_lag,
            "peak_value": c_peak_val,
            "targets": char_stats,
            "false_positive_rate_vs_null_max": fp_char,
        },
    }


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    ensure_publication_inputs(
        voynich_path=args.input,
        allow_placeholder_inputs=args.allow_placeholder_inputs,
    )

    lines = read_takahashi_lines(args.input)

    variants = [
        "alpha_split",
        "alpha_keep_dots",
        "alpha_collapse_runs",
        "alpha_min_len_2",
    ]

    results = {
        "input_file": args.input,
        "seed": args.seed,
        "permutations": args.permutations,
        "target_word_distance": args.target_word_distance,
        "target_char_lags": args.target_char_lags,
        "variants": {},
    }

    print("=" * 80)
    print("PERIODICITY ROBUSTNESS AUDIT")
    print("=" * 80)

    for v in variants:
        words = build_tokens(lines, v)
        vres = evaluate_variant(
            words=words,
            target_word_distance=args.target_word_distance,
            target_char_lags=args.target_char_lags,
            max_word_lag=args.max_word_lag,
            max_char_lag=args.max_char_lag,
            permutations=args.permutations,
        )
        results["variants"][v] = vres

        wp = vres["word_profile"]
        print(
            f"[{v}] tokens={vres['counts']['tokens']:,} | "
            f"word-lag-{args.target_word_distance}={wp['target_observed']:.6f} "
            f"(rank {wp['target_rank']}, p={wp['p_value_ge']:.6f}, z={wp['z_score']:+.3f}, fp_max={wp['false_positive_rate_vs_null_max']:.6f})"
        )

        for lag in args.target_char_lags:
            cs = vres["char_profile"]["targets"][str(lag)]
            print(
                f"    char-lag-{lag}={cs['observed']:+.6f} "
                f"(rank {cs['rank_in_char_profile']}, p={cs['p_value_ge']:.6f}, z={cs['z_score']:+.3f}, fp_max={vres['char_profile']['false_positive_rate_vs_null_max'][str(lag)]:.6f})"
            )

    print("=" * 80)

    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"JSON results written to: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
