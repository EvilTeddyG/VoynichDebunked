# Run Provenance Standard

## Scope

This standard defines the minimum provenance payload required for any claim-facing artifact batch in this repository.

## Required Outputs Per Claim-Facing Batch

1. Machine-readable run manifest
- Path: `artifacts/run_manifest_latest.json`
- Required fields:
  - UTC generation timestamp
  - git commit SHA and branch
  - Python version and executable
  - SHA-256 hashes for frozen inputs
  - SHA-256 hashes and byte sizes for generated artifacts
  - canonical command bundle used to reproduce the batch

2. Human-readable claim mapping
- Path: `docs/results/artifact_claim_index.md`
- Required content:
  - each claim-facing statement linked to generating artifact(s)
  - explicit confidence tier / claim level
  - explicit non-claims and out-of-scope boundaries

3. Section-phase diagnostic bundle (if section claims are made)
- Required artifacts:
  - `artifacts/section_lag_spectrum_compare_min800.json`
  - `artifacts/phase_shift_test_min800_v2.json`
- Required memo:
  - `docs/results/phase_shift_hypothesis_isolation.md`

## Input Freeze Requirements

1. Transcript and control registry hashes must be present in the run manifest.
- `data/takahashi_eva.txt`
- `data/baselines/manifest_template.csv`
- `data/baselines/SOURCES.md`

2. Placeholder input guardrails must remain active for claim-facing scripts.
- Publication-mode default: fail when placeholder corpora are detected.
- Demo-mode override: explicit `--allow-placeholder-inputs` only.

## Promotion Rules (Internal)

A result batch can be promoted to claim-facing only if all conditions are met:

1. Inputs frozen via SHA-256 in `run_manifest_latest.json`.
2. Artifact hashes recorded for all cited outputs.
3. Claim text linked in `artifact_claim_index.md`.
4. Uncertainty/null context present (effect size + uncertainty + false-positive behavior).
5. Claim-boundary language preserved (no authorship/motive escalation without independent convergence).

## Versioning

- Current standard version: `v1.0`
- This file should be updated only when provenance requirements change, not when individual results change.
