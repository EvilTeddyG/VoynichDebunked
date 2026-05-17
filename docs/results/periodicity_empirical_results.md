# Periodicity Empirical Output Snapshot

This document exposes the current periodicity output landscape from the repository pipeline, including strong, weak, and ambiguous regions.

## Data Provenance (Critical)

- Voynich input used in this run: [data/takahashi_eva.txt](../../data/takahashi_eva.txt)
- Current file contents are the historical folio-tagged Takahashi transcript, not the former synthetic fallback.
- Control corpora in this run are external texts listed in [data/baselines/manifest_template.csv](../../data/baselines/manifest_template.csv) with source provenance in [data/baselines/SOURCES.md](../../data/baselines/SOURCES.md).

Interpretation consequence:
- Voynich and control inputs are both externalized from repository-generated placeholder prose.
- Inference quality still depends on control-family suitability and balancing, but this run is no longer blocked by placeholder-control provenance.

## Generated Artifacts

Primary numeric outputs:
- [artifacts/lag_spectrum_compare.csv](../../artifacts/lag_spectrum_compare.csv)
- [artifacts/lag_spectrum_compare.json](../../artifacts/lag_spectrum_compare.json)
- [artifacts/periodicity_robustness.json](../../artifacts/periodicity_robustness.json)
- [artifacts/section_lag_spectrum_compare.csv](../../artifacts/section_lag_spectrum_compare.csv)
- [artifacts/section_lag_spectrum_compare.json](../../artifacts/section_lag_spectrum_compare.json)
- [artifacts/preprocessing_sensitivity.csv](../../artifacts/preprocessing_sensitivity.csv)
- [artifacts/preprocessing_sensitivity.json](../../artifacts/preprocessing_sensitivity.json)

Visual outputs:
- [artifacts/plots/lag_spectra_comparative.png](../../artifacts/plots/lag_spectra_comparative.png)
- [artifacts/plots/lag_spectra_family_aggregate.png](../../artifacts/plots/lag_spectra_family_aggregate.png)
- [artifacts/plots/lag_spectra_periodogram.png](../../artifacts/plots/lag_spectra_periodogram.png)
- [artifacts/plots/voynich_null_hist_lag5.png](../../artifacts/plots/voynich_null_hist_lag5.png)
- [artifacts/plots/voynich_null_hist_lag6.png](../../artifacts/plots/voynich_null_hist_lag6.png)
- [artifacts/plots/voynich_null_hist_lag12.png](../../artifacts/plots/voynich_null_hist_lag12.png)
- [artifacts/plots/voynich_null_hist_lag13.png](../../artifacts/plots/voynich_null_hist_lag13.png)
- [artifacts/plots/section_spectra_grid.png](../../artifacts/plots/section_spectra_grid.png)
- [artifacts/plots/preprocessing_sensitivity_heatmap.png](../../artifacts/plots/preprocessing_sensitivity_heatmap.png)

## Lag-Spectrum Results (Voynich Record in Current Run)

Source: [artifacts/lag_spectrum_compare.json](../../artifacts/lag_spectrum_compare.json)

- Global peak lag: 6
- Global peak value: 0.03332516743

Target lags requested for scrutiny:

| Lag | Observed | z-score | p-value (null >= observed) | Rank in profile | Null 95% band |
|---|---:|---:|---:|---:|---|
| 5  | +0.02070060 | +38.7182 | 0.00498 | 2  | [-0.00099721, +0.00101281] |
| 6  | +0.03332517 | +55.4263 | 0.00498 | 1  | [-0.00120566, +0.00111763] |
| 12 | +0.01723213 | +29.0606 | 0.00498 | 3  | [-0.00131819, +0.00098428] |
| 13 | +0.01397468 | +25.5184 | 0.00498 | 6  | [-0.00102543, +0.00099512] |

Interpretation from these values:
- The raw unsegmented character stream shows strong periodicity at lags 5, 6, 12, and 13.
- The strongest global peak is lag 6, with lag 5 second.
- These raw spectral peaks should be read alongside perturbation panels below, which test whether conclusions survive alternate preprocessing choices.

## Section-Level Stability (Current Run)

Source: [artifacts/section_lag_spectrum_compare.json](../../artifacts/section_lag_spectrum_compare.json)

- Section retention threshold: 3,000 characters.
- Retained sections: 2 historical sections (`108v`, `111r`).
- Both retained sections have peak lag 6 under the current section-threshold run.

Section-level interpretation in this run:

- Section retention is now based on historical folio groups rather than synthetic `SIM` tags.
- With the current `min_section_chars` threshold, only two sections are retained, so this panel is still sparse rather than manuscript-wide.
- The regenerated section plot is [artifacts/plots/section_spectra_grid.png](../../artifacts/plots/section_spectra_grid.png).

## Preprocessing Sensitivity (Assumption Drift)

Source: [artifacts/preprocessing_sensitivity.json](../../artifacts/preprocessing_sensitivity.json)

Drift envelope by target lag across normalization variants:

| Lag | z-range | p-value range | Rank range |
|---|---:|---:|---:|
| 5  | 6.6679 | [0.00332, 0.85714] | [2, 40] |
| 6  | 2.7841 | [0.77076, 1.00000] | [41, 56] |
| 12 | 3.7894 | [0.05316, 0.99003] | [9, 53] |
| 13 | 3.4748 | [0.10299, 0.99336] | [9, 54] |

Interpretation:
- Lag 5 is highly sensitive to preprocessing assumptions: strongly elevated in three variants but weak/negative in one (`alpha_min_len_2`).
- Lag 6 remains consistently unsupported across variants.
- Lags 12 and 13 are unstable across preprocessing choices and do not present robust dominant behavior in this run.

This panel is intentionally included to expose model fragility zones where conclusions can reverse under plausible preprocessing choices.

## Tokenization Robustness (Ambiguity and Failure Exposure)

Source: [artifacts/periodicity_robustness.json](../../artifacts/periodicity_robustness.json)

Word-distance target (13):
- alpha_split: z=+20.530, p=0.00249, rank=3
- alpha_keep_dots: z=+7.291, p=0.00249, rank=10
- alpha_collapse_runs: z=+21.128, p=0.00249, rank=6
- alpha_min_len_2: z=+16.938, p=0.00249, rank=15

Character lag 5:
- alpha_split: z=+36.744, p=0.00249, rank=2, null-max FPR=0.00249
- alpha_keep_dots: z=+35.401, p=0.00249, rank=2, null-max FPR=0.00249
- alpha_collapse_runs: z=+53.183, p=0.00249, rank=1, null-max FPR=0.00249
- alpha_min_len_2: z=+34.442, p=0.00249, rank=2, null-max FPR=0.00249

Character lag 6:
- alpha_split: z=+55.106, p=0.00249, rank=1, null-max FPR=0.00249
- alpha_keep_dots: z=+56.416, p=0.00249, rank=1, null-max FPR=0.00249
- alpha_collapse_runs: z=+36.030, p=0.00249, rank=2, null-max FPR=0.00249
- alpha_min_len_2: z=+57.855, p=0.00249, rank=1, null-max FPR=0.00249

Interpretation from robustness panel:
- The 13-word target is strongly elevated relative to null in all four variants.
- Character lags 5 and 6 are strongly elevated in all four variants, and both are near-profile maxima in each variant.
- This panel now supports robust character-lag and word-distance signals under its variant family.
- However, this does not erase the preprocessing-sensitivity panel above, which probes a different perturbation family and still shows instability for lag-6 under those alternate assumptions.

## Control-Family Context

The comparative and family-aggregate spectra provide shape-level checks rather than single-value claims:
- [artifacts/plots/lag_spectra_comparative.png](../../artifacts/plots/lag_spectra_comparative.png)
- [artifacts/plots/lag_spectra_family_aggregate.png](../../artifacts/plots/lag_spectra_family_aggregate.png)
- [artifacts/plots/lag_spectra_periodogram.png](../../artifacts/plots/lag_spectra_periodogram.png)

What to inspect visually:
- Whether the Voynich curve is isolated or accompanied by similarly strong neighboring peaks.
- Whether spectral density shows one dominant narrow-band feature or a broader noisy field.
- Whether family curves overlap Voynich in shape and amplitude regimes.

## Current Bottom Line

What is supported by this run:
- The pipeline now exposes full empirical terrain: spectra, null histograms, confidence bands, robustness variants, and family comparison views.
- Strong lag-5 and lag-6 character anomalies appear in the global spectrum and in the tokenization-robustness panel.
- The 13-word distance statistic is elevated in the tokenization-robustness panel.

What is not supported by this run:
- A single preprocessing-invariant conclusion across all perturbation families.
- Section-wide stability across many folio groups (only two sections exceed the current threshold).

Most important limitation to resolve next:
- Harmonize and document the difference between preprocessing-sensitivity and tokenization-robustness variant definitions, then rerun both panels under one shared perturbation policy.
- Expand and rebalance control families (more independent corpora per family) before treating any one nearest-neighbor relationship as publication-grade historical exclusion.

