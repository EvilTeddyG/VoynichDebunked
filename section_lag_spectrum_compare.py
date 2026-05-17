#!/usr/bin/env python3
"""
Section-stratified lag-spectrum comparison for Voynich plus global controls.

Outputs:
- Long CSV for plotting per section and controls.
- JSON summary with per-section target-lag stats, peak lags, and null envelopes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
from collections import Counter, defaultdict
from statistics import mean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Section-stratified null-calibrated lag spectra")
    parser.add_argument("--voynich", default="data/takahashi_eva.txt", help="Voynich transcript path")
    parser.add_argument("--manifest", default="data/baselines/manifest_template.csv", help="Control manifest CSV")
    parser.add_argument("--max-lag", type=int, default=60, help="Maximum lag for spectra")
    parser.add_argument("--target-lags", nargs="+", type=int, default=[5, 6, 12, 13], help="Lags to summarize")
    parser.add_argument("--permutations", type=int, default=200, help="Null permutations per profile")
    parser.add_argument("--min-section-chars", type=int, default=3000, help="Minimum chars needed to keep a section")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--csv-out", default="artifacts/section_lag_spectrum_compare.csv", help="Output long CSV")
    parser.add_argument("--json-out", default="artifacts/section_lag_spectrum_compare.json", help="Output summary JSON")
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


def resolve_path(base_manifest: str, rel_or_abs: str) -> str:
    if os.path.isabs(rel_or_abs):
        return rel_or_abs
    return os.path.normpath(os.path.join(os.path.dirname(base_manifest), rel_or_abs))


def read_manifest(path: str) -> list[dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("label") and row.get("path") and row.get("family"):
                rows.append(row)
    return rows


def normalize_words(text: str) -> list[str]:
    toks = [re.sub(r"[^a-zA-Z]", "", w).strip() for w in re.split(r"[\s.-]", text)]
    return [w for w in toks if w]


def words_to_chars(words: list[str]) -> list[str]:
    return [c for w in words for c in w if c.isalpha()]


def parse_voynich_tag(line: str) -> tuple[str | None, str]:
    m = re.match(r"\s*<f([^>]+)>\s*(.*)$", line)
    if not m:
        return None, ""
    tag = m.group(1).strip()
    content = m.group(2).strip()
    # Section key is the tag prefix before first dot/space (e.g., 1r, 1v, SIM).
    section = re.split(r"[.\s]", tag)[0]
    section = section if section else "unknown"
    return section, content


def extract_voynich_section_chars(path: str) -> tuple[list[str], dict[str, list[str]]]:
    global_words: list[str] = []
    by_section_words: dict[str, list[str]] = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            if not raw.startswith("<f"):
                continue
            section, content = parse_voynich_tag(raw)
            if section is None:
                continue
            words = normalize_words(content)
            global_words.extend(words)
            by_section_words[section].extend(words)
    global_chars = words_to_chars(global_words)
    by_section_chars = {k: words_to_chars(v) for k, v in by_section_words.items()}
    return global_chars, by_section_chars


def extract_control_chars(path: str) -> list[str]:
    words: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            words.extend(normalize_words(raw.strip()))
    return words_to_chars(words)


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


def rank_lag(profile: dict[int, float], lag: int) -> int:
    ranked = sorted(profile.items(), key=lambda kv: kv[1], reverse=True)
    for i, (k, _) in enumerate(ranked, start=1):
        if k == lag:
            return i
    return len(ranked) + 1


def build_profile_stats(chars: list[str], max_lag: int, target_lags: list[int], permutations: int) -> tuple[dict, list[dict]]:
    obs = lag_profile(chars, max_lag)

    null_by_lag = {lag: [] for lag in range(1, max_lag + 1)}
    for _ in range(permutations):
        shuffled = chars[:]
        random.shuffle(shuffled)
        prof = lag_profile(shuffled, max_lag)
        for lag, v in prof.items():
            null_by_lag[lag].append(v)

    target_stats = {}
    rows = []
    for lag in range(1, max_lag + 1):
        vals = null_by_lag[lag]
        vals_sorted = sorted(vals)
        nm = mean(vals) if vals else 0.0
        ns = stddev(vals)
        ov = obs[lag]
        z = (ov - nm) / ns if ns > 0 else 0.0

        rows.append(
            {
                "lag": lag,
                "observed": ov,
                "null_mean": nm,
                "null_q025": percentile(vals_sorted, 2.5),
                "null_q975": percentile(vals_sorted, 97.5),
                "z_score": z,
            }
        )

    for lag in target_lags:
        vals = null_by_lag.get(lag, [])
        vals_sorted = sorted(vals)
        nm = mean(vals) if vals else 0.0
        ns = stddev(vals)
        ov = obs.get(lag, 0.0)
        p = (sum(1 for x in vals if x >= ov) + 1) / (len(vals) + 1) if vals else 1.0
        z = (ov - nm) / ns if ns > 0 else 0.0
        target_stats[str(lag)] = {
            "observed": ov,
            "null_mean": nm,
            "null_sd": ns,
            "null_q025": percentile(vals_sorted, 2.5),
            "null_q975": percentile(vals_sorted, 97.5),
            "p_value_ge": p,
            "z_score": z,
            "rank": rank_lag(obs, lag),
        }

    stats = {
        "char_count": len(chars),
        "observed_profile": [obs[lag] for lag in range(1, max_lag + 1)],
        "peak_lag": max(obs, key=lambda k: obs[k]) if obs else None,
        "peak_value": max(obs.values()) if obs else 0.0,
        "target_lag_stats": target_stats,
    }
    return stats, rows


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    global_chars, by_section_chars = extract_voynich_section_chars(args.voynich)
    if not global_chars:
        print("ERROR: no Voynich lines parsed; expected <f...> tagged lines")
        return 1

    kept_sections = {
        k: chars for k, chars in by_section_chars.items() if len(chars) >= args.min_section_chars
    }

    long_rows = []
    summary = {
        "max_lag": args.max_lag,
        "target_lags": args.target_lags,
        "min_section_chars": args.min_section_chars,
        "voynich_global": {},
        "voynich_sections": [],
        "controls": [],
    }

    # Voynich global profile.
    global_stats, global_rows = build_profile_stats(global_chars, args.max_lag, args.target_lags, args.permutations)
    summary["voynich_global"] = global_stats
    for row in global_rows:
        long_rows.append(
            {
                "group": "voynich_global",
                "label": "voynich_global",
                "family": "voynich",
                "section": "global",
                **row,
            }
        )

    # Voynich section profiles.
    for section in sorted(kept_sections.keys()):
        stats, rows = build_profile_stats(kept_sections[section], args.max_lag, args.target_lags, args.permutations)
        summary["voynich_sections"].append({"section": section, **stats})
        for row in rows:
            long_rows.append(
                {
                    "group": "voynich_section",
                    "label": f"voynich_{section}",
                    "family": "voynich",
                    "section": section,
                    **row,
                }
            )

    # Global controls from manifest.
    for item in read_manifest(args.manifest):
        p = resolve_path(args.manifest, item["path"])
        if not os.path.exists(p):
            continue
        chars = extract_control_chars(p)
        if not chars:
            continue

        stats, rows = build_profile_stats(chars, args.max_lag, args.target_lags, args.permutations)
        summary["controls"].append({"label": item["label"], "family": item["family"], "path": p, **stats})
        for row in rows:
            long_rows.append(
                {
                    "group": "control",
                    "label": item["label"],
                    "family": item["family"],
                    "section": "global",
                    **row,
                }
            )

    if not summary["controls"]:
        print("ERROR: no control corpora resolved")
        return 1

    os.makedirs(os.path.dirname(args.csv_out), exist_ok=True)
    with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "label",
                "family",
                "section",
                "lag",
                "observed",
                "null_mean",
                "null_q025",
                "null_q975",
                "z_score",
            ],
        )
        w.writeheader()
        w.writerows(long_rows)

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("=" * 80)
    print("SECTION LAG SPECTRUM COMPARISON COMPLETE")
    print("=" * 80)
    print(f"Voynich sections retained: {len(summary['voynich_sections'])}")
    print(f"Controls: {len(summary['controls'])}")
    print(f"CSV: {args.csv_out}")
    print(f"JSON: {args.json_out}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
