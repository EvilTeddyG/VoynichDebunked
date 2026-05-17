#!/usr/bin/env python3
"""
Convert manual folio geometry measurement sheet (CSV) to scorer JSON schema.

Expected CSV columns:
- folio
- feature
- value
- unit (optional)
- method (optional)
- rater (optional)
- notes (optional)

Supported features:
- spoke_count
- ring_count
- zodiac_divisions
- ring_spacing_cv
- occlusion_phase
- calibration_density
"""

from __future__ import annotations

import argparse
import csv
import json
import os


ALLOWED = {
    "spoke_count",
    "ring_count",
    "zodiac_divisions",
    "ring_spacing_cv",
    "occlusion_phase",
    "calibration_density",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert folio geometry CSV to JSON schema")
    p.add_argument("--csv", default="data/astronomy/folio_geometry_measurement_sheet_template.csv", help="Input measurement CSV")
    p.add_argument("--json-out", default="data/astronomy/folio_geometry_measured.json", help="Output JSON for scorer")
    return p.parse_args()


def main() -> int:
    by_folio = {}

    with open(args.csv, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        missing = {"folio", "feature", "value"} - set(r.fieldnames or [])
        if missing:
            print(f"ERROR: missing required columns: {sorted(missing)}")
            return 1
        for row in r:
            folio = (row.get("folio") or "").strip()
            feat = (row.get("feature") or "").strip()
            val_raw = (row.get("value") or "").strip()
            if not folio or not feat or not val_raw:
                continue
            if feat not in ALLOWED:
                continue
            try:
                val = float(val_raw)
            except ValueError:
                continue
            rec = by_folio.setdefault(folio, {"folio": folio})
            rec[feat] = int(val) if feat in {"spoke_count", "ring_count", "zodiac_divisions"} else float(val)

    folios = []
    required = {"spoke_count", "ring_count", "zodiac_divisions", "ring_spacing_cv", "occlusion_phase", "calibration_density"}
    for folio in sorted(by_folio.keys()):
        rec = by_folio[folio]
        if required.issubset(set(rec.keys())):
            folios.append(rec)

    if not folios:
        print("ERROR: no complete folio records found after conversion")
        return 1

    out = {
        "metadata": {
            "description": "Measured folio geometry converted from manual CSV sheet",
            "source_csv": args.csv,
        },
        "folios": folios,
    }

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=" * 80)
    print("FOLIO GEOMETRY CSV->JSON CONVERSION COMPLETE")
    print("=" * 80)
    print(f"Folios converted: {len(folios)}")
    print(f"JSON: {args.json_out}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main())
