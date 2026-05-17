#!/usr/bin/env python3
"""
Fetch a Takahashi/EVA transcript file reproducibly.

Usage examples:
  python fetch_takahashi.py \
    --url "https://example.org/takahashi.txt" \
    --output data/takahashi_eva.txt

  python fetch_takahashi.py \
    --url "https://example.org/takahashi.txt" \
    --output data/takahashi_eva.txt \
    --sha256 <expected_hash>
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import urllib.request


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Takahashi transcript with optional hash verification")
    parser.add_argument("--url", required=True, help="Direct URL to transcript text file")
    parser.add_argument("--output", required=True, help="Output path for downloaded transcript")
    parser.add_argument(
        "--sha256",
        default=None,
        help="Optional expected SHA-256 for deterministic verification",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        with urllib.request.urlopen(args.url, timeout=args.timeout) as response:
            data = response.read()
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return 1

    digest = sha256_bytes(data)

    if args.sha256 and digest.lower() != args.sha256.lower():
        print("ERROR: SHA-256 mismatch", file=sys.stderr)
        print(f"  expected: {args.sha256}", file=sys.stderr)
        print(f"  actual:   {digest}", file=sys.stderr)
        return 2

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)

    print(f"Saved: {output_path}")
    print(f"Bytes: {len(data)}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
