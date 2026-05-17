# Artifact-to-Claim Index

This index maps claim-facing statements to their generating artifacts and confidence tier.

## Tier Definitions

- Tier A: Strong process-level evidence with robust null context and reproducible artifacts.
- Tier B: Supported but conditional evidence; sensitive to assumptions or partition definitions.
- Tier C: Exploratory/descriptive signal; not suitable as a core theorem anchor.

## Claims and Evidence Links

1. Claim: Voynich shows unusually low conditional entropy relative to natural-language baselines.
- Tier: A
- Primary artifacts:
  - `artifacts/cryptanalysis_metrics.json`
  - `docs/research/voynich_scientific_proof.md`
- Notes:
  - Treated as central process-class axis in current boundary language.

2. Claim: Strong positional dependence / line-effect structure exists.
- Tier: A
- Primary artifacts:
  - `artifacts/cryptanalysis_metrics.json`
  - `docs/research/voynich_stencil_proof.md`
- Notes:
  - Supports constrained procedural behavior; does not identify mechanism identity.

3. Claim: Global lag spectra show strong peaks including lag 5 and lag 6 in the current canonical run.
- Tier: B
- Primary artifacts:
  - `artifacts/lag_spectrum_compare.json`
  - `artifacts/lag_spectrum_compare.csv`
  - `artifacts/plots/lag_spectra_comparative.png`
- Notes:
  - Global-curve claims are conditioned on preprocessing assumptions and section composition.

4. Claim: Early-vs-late section heterogeneity is present; late folios show higher lag-6 concentration under min-800 section test.
- Tier: B
- Primary artifacts:
  - `artifacts/section_lag_spectrum_compare_min800.json`
  - `artifacts/phase_shift_test_min800_v2.json`
  - `docs/results/phase_shift_hypothesis_isolation.md`
- Notes:
  - Supported in quartile-window tests and trimmed variants; single global lag-6 changepoint is not yet significant.

5. Claim: Roughness-oriented changepoint near 111r/111v is statistically credible.
- Tier: B
- Primary artifacts:
  - `artifacts/phase_shift_test_min800_v2.json`
  - `docs/results/phase_shift_hypothesis_isolation.md`
- Notes:
  - This is a structure-transition indicator, not a mechanism-identification proof.

6. Claim: Word-lag-13 is descriptive/exploratory and outside core formal boundary.
- Tier: C
- Primary artifacts:
  - `artifacts/periodicity_robustness.json`
  - `docs/results/periodicity_empirical_results.md`
- Notes:
  - Not used as a core theorem anchor.

## Non-Claims (Explicit)

The current repository does not claim:

1. Authorship identification.
2. Motive reconstruction.
3. Definitive historical attribution from astronomy scoring alone.
4. Full plaintext translation.

## Manifest Link

This index is tied to the current frozen run manifest:
- `artifacts/run_manifest_latest.json`
