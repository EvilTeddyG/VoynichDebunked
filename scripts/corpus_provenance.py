#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass


PLACEHOLDER_TEXT_MARKERS = (
    "voynich",
    "beinecke",
    "synthetic",
    "markov",
    "comparative audit",
    "mechanical generation",
    "mechanical-generation",
)


@dataclass
class ProvenanceIssue:
    scope: str
    path: str
    code: str
    message: str


def _read_head(path: str, limit: int = 4096) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read(limit)


def inspect_voynich_transcript(path: str) -> list[ProvenanceIssue]:
    issues: list[ProvenanceIssue] = []
    first_tag = None

    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.startswith("<f"):
                continue
            match = re.match(r"\s*<f([^>]+)>", raw)
            if match:
                first_tag = match.group(1).strip()
            break

    if first_tag is None:
        issues.append(
            ProvenanceIssue(
                scope="voynich",
                path=path,
                code="missing_transcript_tags",
                message="No Takahashi-style <f...> transcript lines were found.",
            )
        )
        return issues

    if first_tag.upper().startswith("SIM"):
        issues.append(
            ProvenanceIssue(
                scope="voynich",
                path=path,
                code="synthetic_transcript",
                message="Transcript begins with <fSIM...> synthetic fallback content, not a canonical historical transcript.",
            )
        )

    return issues


def inspect_control_manifest(path: str) -> list[ProvenanceIssue]:
    issues: list[ProvenanceIssue] = []

    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            label = row.get("label", "")
            notes = (row.get("notes") or "").strip()
            if "placeholder" in notes.lower() or "repository-derived" in notes.lower():
                issues.append(
                    ProvenanceIssue(
                        scope="controls",
                        path=path,
                        code="placeholder_manifest_entry",
                        message=f"Manifest entry '{label}' is marked as a repository-derived placeholder control.",
                    )
                )

    return issues


def inspect_control_directory(path: str) -> list[ProvenanceIssue]:
    issues: list[ProvenanceIssue] = []

    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        if not os.path.isfile(full) or not name.lower().endswith(".txt"):
            continue
        head = _read_head(full).lower()
        marker_hits = sum(1 for marker in PLACEHOLDER_TEXT_MARKERS if marker in head)
        if marker_hits >= 2:
            issues.append(
                ProvenanceIssue(
                    scope="controls",
                    path=full,
                    code="placeholder_control_text",
                    message=f"Control corpus '{name}' appears to contain repository prose or synthetic-analysis text rather than an external corpus.",
                )
            )

    return issues


def ensure_publication_inputs(
    *,
    voynich_path: str,
    manifest_path: str | None = None,
    corpora_dir: str | None = None,
    allow_placeholder_inputs: bool = False,
) -> None:
    issues = inspect_voynich_transcript(voynich_path)
    if manifest_path:
        issues.extend(inspect_control_manifest(manifest_path))
    if corpora_dir:
        issues.extend(inspect_control_directory(corpora_dir))

    if not issues:
        return

    lines = [
        "Refusing to run claim-facing analysis on placeholder corpus inputs.",
        "Use canonical transcript/control corpora, or rerun with --allow-placeholder-inputs for demo-only validation.",
    ]
    for issue in issues:
        lines.append(f"- [{issue.code}] {issue.message} ({issue.path})")

    if allow_placeholder_inputs:
        print("WARNING: placeholder inputs explicitly allowed")
        for line in lines[2:]:
            print(line)
        return

    raise ValueError("\n".join(lines))