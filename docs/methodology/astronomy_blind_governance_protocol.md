# Astronomy Blind Governance Protocol

## Status

This protocol is active for astronomy-layer claim handling.

## Purpose

Preserve epistemic separation between geometry-scoring outputs and stronger process-class claims by enforcing preregistered blind procedures and interpretation boundaries.

## Freeze Rules (Before Unblinding)

1. Freeze scoring configuration.
- Feature set
- Weighting constants
- Similarity epsilon
- Null-generation definitions

2. Freeze candidate table and date window for the run.

3. Freeze interpretation note prior to opening blind key.
- Must include allowed and disallowed claim levels.

4. Freeze acceptance thresholds.
- Best-vs-runner-up gap checks
- Near-tie reporting rules
- Null rarity interpretation rule

## Required Blind Outputs

1. Blind run outputs:
- `artifacts/astronomy_candidate_scores_blind.csv`
- `artifacts/astronomy_overlay_report_blind.json`
- `artifacts/astronomy_blind_key.json`

2. Unblinded run outputs:
- `artifacts/astronomy_candidate_scores.csv`
- `artifacts/astronomy_overlay_report.json`

## Disclosure Requirements

1. Publish full ranking surface, not top hit only.
2. Publish null calibration diagnostics and near-ties.
3. Publish false-match behavior and sensitivity notes.
4. Preserve explicit boundary language:
- Allowed: constrained historical dependence inference.
- Not allowed: authorship identification or definitive production-date proof.

## Governance Separation

Astronomy layer must not be used to upgrade process-class claims unless independent non-astronomy evidence converges.

## Preregistration Link

Use and update:
- `docs/methodology/astronomy_preregistration_template.md`
