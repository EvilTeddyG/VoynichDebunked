#!/usr/bin/env python3
"""
Geometric candidate scoring for the Anchor-Truth eclipse hypothesis.

This script scores folio geometry feature vectors against candidate eclipse/event
feature vectors, then calibrates match rarity under a null generator.

Outputs:
- CSV ranking of candidate events.
- JSON report with best-fit candidate, null distribution, and per-feature deltas.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
from statistics import mean


SCALES = {
    "spoke_count": 12.0,
    "ring_count": 6.0,
    "zodiac_divisions": 12.0,
    "occlusion_phase": 1.0,
    "calibration_density": 1.0,
}

WEIGHTS = {
    "spoke_count": 1.8,
    "ring_count": 1.2,
    "zodiac_divisions": 1.8,
    "occlusion_phase": 1.4,
    "calibration_density": 1.0,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score folio geometry against eclipse/event candidates")
    p.add_argument("--folio-json", default="data/astronomy/folio_geometry_template.json", help="Folio feature JSON")
    p.add_argument("--candidate-csv", default="data/astronomy/eclipse_candidates_template.csv", help="Candidate event CSV")
    p.add_argument("--date-window-start", type=int, default=1404, help="Lower bound on event year")
    p.add_argument("--date-window-end", type=int, default=1438, help="Upper bound on event year")
    p.add_argument("--null-samples", type=int, default=5000, help="Null samples for rarity calibration")
    p.add_argument("--seed", type=int, default=42, help="RNG seed")
    p.add_argument("--blind", action="store_true", help="Blind candidate identities in public outputs")
    p.add_argument(
        "--blind-key-out",
        default="artifacts/astronomy_blind_key.json",
        help="Where to store candidate-code unblinding key (used only with --blind)",
    )
    p.add_argument("--csv-out", default="artifacts/astronomy_candidate_scores.csv", help="Output ranking CSV")
    p.add_argument("--json-out", default="artifacts/astronomy_overlay_report.json", help="Output report JSON")
    return p.parse_args()


def _safe_float(x: str | float | int) -> float:
    return float(x)


def load_folio_json(path: str) -> list[dict[str, float | str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    folios = data.get("folios", [])
    if not folios:
        raise ValueError("No folios in folio JSON")
    return folios


def load_candidates(path: str, y0: int, y1: int) -> list[dict[str, float | str | int]]:
    rows: list[dict[str, float | str | int]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            year = int(row["year"])
            if year < y0 or year > y1:
                continue
            rows.append(
                {
                    "event_id": row["event_id"],
                    "date": row["date"],
                    "year": year,
                    "event_type": row.get("event_type", "unknown"),
                    "visibility_n_italy": _safe_float(row["visibility_n_italy"]),
                    "magnitude_n_italy": _safe_float(row["magnitude_n_italy"]),
                    "spoke_count_expected": _safe_float(row["spoke_count_expected"]),
                    "ring_count_expected": _safe_float(row["ring_count_expected"]),
                    "zodiac_divisions_expected": _safe_float(row["zodiac_divisions_expected"]),
                    "occlusion_phase_expected": _safe_float(row["occlusion_phase_expected"]),
                    "calibration_density_expected": _safe_float(row["calibration_density_expected"]),
                }
            )
    if not rows:
        raise ValueError("No candidates in requested date window")
    return rows


def feature_weighted_distance(folio: dict, cand: dict) -> tuple[float, dict[str, float]]:
    deltas = {
        "spoke_count": (float(folio["spoke_count"]) - float(cand["spoke_count_expected"])) / SCALES["spoke_count"],
        "ring_count": (float(folio["ring_count"]) - float(cand["ring_count_expected"])) / SCALES["ring_count"],
        "zodiac_divisions": (float(folio["zodiac_divisions"]) - float(cand["zodiac_divisions_expected"])) / SCALES["zodiac_divisions"],
        "occlusion_phase": (float(folio["occlusion_phase"]) - float(cand["occlusion_phase_expected"])) / SCALES["occlusion_phase"],
        "calibration_density": (float(folio["calibration_density"]) - float(cand["calibration_density_expected"])) / SCALES["calibration_density"],
    }

    sq = 0.0
    for k, dv in deltas.items():
        sq += WEIGHTS[k] * dv * dv
    return math.sqrt(sq), {k: abs(v) for k, v in deltas.items()}


def candidate_score(folios: list[dict], cand: dict) -> tuple[float, dict]:
    per_folio = []
    for f in folios:
        d, abs_d = feature_weighted_distance(f, cand)
        per_folio.append({"folio": f["folio"], "distance": d, "feature_abs_delta": abs_d})

    mean_dist = mean(x["distance"] for x in per_folio)

    # Visibility/magnitude modifier rewards candidates observable in N. Italy.
    vis_bonus = 1.0 - 0.15 * float(cand["visibility_n_italy"]) - 0.10 * float(cand["magnitude_n_italy"])
    vis_bonus = max(0.7, min(1.0, vis_bonus))

    final_score = mean_dist * vis_bonus
    return final_score, {"per_folio": per_folio, "mean_distance": mean_dist, "visibility_modifier": vis_bonus}


def random_null_candidate() -> dict[str, float]:
    return {
        "spoke_count_expected": random.uniform(8, 16),
        "ring_count_expected": random.uniform(2, 7),
        "zodiac_divisions_expected": random.uniform(8, 16),
        "occlusion_phase_expected": random.uniform(0.0, 1.0),
        "calibration_density_expected": random.uniform(0.3, 0.9),
        "visibility_n_italy": random.uniform(0.2, 1.0),
        "magnitude_n_italy": random.uniform(0.2, 1.0),
    }


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    i = max(0, min(len(sorted_vals) - 1, int(round((p / 100.0) * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def build_blind_codes(candidates: list[dict], seed: int) -> dict[str, str]:
    ids = [str(c["event_id"]) for c in candidates]
    rng = random.Random(seed + 1001)
    rng.shuffle(ids)
    return {event_id: f"C{idx:03d}" for idx, event_id in enumerate(ids, start=1)}


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    folios = load_folio_json(args.folio_json)
    candidates = load_candidates(args.candidate_csv, args.date_window_start, args.date_window_end)

    ranked = []
    for c in candidates:
        s, details = candidate_score(folios, c)
        ranked.append({
            "event_id": c["event_id"],
            "date": c["date"],
            "year": c["year"],
            "event_type": c["event_type"],
            "score": s,
            "mean_distance": details["mean_distance"],
            "visibility_modifier": details["visibility_modifier"],
            "details": details,
        })

    ranked.sort(key=lambda x: x["score"])
    best = ranked[0]

    blind_codes: dict[str, str] = {}
    if args.blind:
        blind_codes = build_blind_codes(candidates, args.seed)

    null_scores = []
    for _ in range(args.null_samples):
        c = random_null_candidate()
        s, _ = candidate_score(folios, c)
        null_scores.append(s)

    null_sorted = sorted(null_scores)
    null_mean = mean(null_scores)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_scores) / max(1, len(null_scores) - 1))
    p_le = (sum(1 for x in null_scores if x <= best["score"]) + 1) / (len(null_scores) + 1)
    z = (best["score"] - null_mean) / null_sd if null_sd > 0 else 0.0

    os.makedirs(os.path.dirname(args.csv_out), exist_ok=True)
    with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["rank", "event_id", "date", "year", "event_type", "score", "mean_distance", "visibility_modifier"],
        )
        w.writeheader()
        for i, r in enumerate(ranked, start=1):
            public_id = blind_codes.get(r["event_id"], r["event_id"]) if args.blind else r["event_id"]
            public_date = "BLINDED" if args.blind else r["date"]
            public_year = "BLINDED" if args.blind else r["year"]
            public_type = "BLINDED" if args.blind else r["event_type"]
            w.writerow(
                {
                    "rank": i,
                    "event_id": public_id,
                    "date": public_date,
                    "year": public_year,
                    "event_type": public_type,
                    "score": r["score"],
                    "mean_distance": r["mean_distance"],
                    "visibility_modifier": r["visibility_modifier"],
                }
            )

    if args.blind:
        os.makedirs(os.path.dirname(args.blind_key_out), exist_ok=True)
        with open(args.blind_key_out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "warning": "Unblinding key: keep private until ranking decisions are frozen.",
                    "mapping": [
                        {
                            "candidate_code": blind_codes[event_id],
                            "event_id": event_id,
                            "date": next(r["date"] for r in ranked if r["event_id"] == event_id),
                            "year": next(r["year"] for r in ranked if r["event_id"] == event_id),
                        }
                        for event_id in sorted(blind_codes.keys())
                    ],
                },
                f,
                indent=2,
            )

    public_best_id = blind_codes.get(best["event_id"], best["event_id"]) if args.blind else best["event_id"]
    public_best_date = "BLINDED" if args.blind else best["date"]
    public_best_year = "BLINDED" if args.blind else best["year"]

    public_top5 = []
    for r in ranked[:5]:
        public_top5.append(
            {
                "event_id": blind_codes.get(r["event_id"], r["event_id"]) if args.blind else r["event_id"],
                "date": "BLINDED" if args.blind else r["date"],
                "year": "BLINDED" if args.blind else r["year"],
                "event_type": "BLINDED" if args.blind else r["event_type"],
                "score": r["score"],
                "mean_distance": r["mean_distance"],
                "visibility_modifier": r["visibility_modifier"],
                "details": r["details"],
            }
        )

    report = {
        "status": "hypothesis_scaffold",
        "input": {
            "folio_json": args.folio_json,
            "candidate_csv": args.candidate_csv,
            "date_window": [args.date_window_start, args.date_window_end],
            "null_samples": args.null_samples,
            "seed": args.seed,
            "blind_mode": args.blind,
            "blind_key_out": args.blind_key_out if args.blind else None,
            "scoring_config": {
                "scales": SCALES,
                "weights": WEIGHTS,
                "score_semantics": "Lower score indicates closer geometric fit.",
            },
        },
        "best_candidate": {
            "event_id": public_best_id,
            "date": public_best_date,
            "year": public_best_year,
            "score": best["score"],
            "rank": 1,
            "details": best["details"],
        },
        "candidate_ranking_top5": public_top5,
        "null_calibration": {
            "null_mean": null_mean,
            "null_sd": null_sd,
            "null_q025": percentile(null_sorted, 2.5),
            "null_q975": percentile(null_sorted, 97.5),
            "p_value_le": p_le,
            "z_score": z,
            "interpretation": "Lower score is better fit; p_value_le is rarity under null random geometry.",
        },
        "warning": "This report is only as valid as feature extraction quality; template values are placeholders until replaced with measured folio geometry.",
    }

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=" * 80)
    print("ASTRONOMICAL GEOMETRY SCORING COMPLETE")
    print("=" * 80)
    print(f"Candidates in window: {len(candidates)}")
    print(f"Best candidate: {public_best_id} ({public_best_date}) score={best['score']:.6f}")
    print(f"Null p_value_le={p_le:.6g}, z={z:+.3f}")
    print(f"CSV: {args.csv_out}")
    print(f"JSON: {args.json_out}")
    if args.blind:
        print(f"Blind key: {args.blind_key_out}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
