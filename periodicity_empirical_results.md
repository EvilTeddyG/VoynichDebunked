# Periodicity Empirical Output Snapshot

This document exposes the current periodicity output landscape from the repository pipeline, including strong, weak, and ambiguous regions.

## Data Provenance (Critical)

- Voynich input used in this run: [data/takahashi_eva.txt](data/takahashi_eva.txt)
- Current file contents indicate a synthetic fallback transcript (`<fSIM...>` lines), not a downloaded canonical Takahashi source.
- Control corpora in this run are repository-derived placeholders listed in [data/baselines/manifest_template.csv](data/baselines/manifest_template.csv).

Interpretation consequence:
- These outputs are an empirical pipeline demonstration, not final manuscript-grade evidence against historical corpora.

## Generated Artifacts

Primary numeric outputs:
- [artifacts/lag_spectrum_compare.csv](artifacts/lag_spectrum_compare.csv)
- [artifacts/lag_spectrum_compare.json](artifacts/lag_spectrum_compare.json)
- [artifacts/periodicity_robustness.json](artifacts/periodicity_robustness.json)

Visual outputs:
- [artifacts/plots/lag_spectra_comparative.png](artifacts/plots/lag_spectra_comparative.png)
- [artifacts/plots/lag_spectra_family_aggregate.png](artifacts/plots/lag_spectra_family_aggregate.png)
- [artifacts/plots/lag_spectra_periodogram.png](artifacts/plots/lag_spectra_periodogram.png)
- [artifacts/plots/voynich_null_hist_lag5.png](artifacts/plots/voynich_null_hist_lag5.png)
- [artifacts/plots/voynich_null_hist_lag6.png](artifacts/plots/voynich_null_hist_lag6.png)
- [artifacts/plots/voynich_null_hist_lag12.png](artifacts/plots/voynich_null_hist_lag12.png)
- [artifacts/plots/voynich_null_hist_lag13.png](artifacts/plots/voynich_null_hist_lag13.png)

## Lag-Spectrum Results (Voynich Record in Current Run)

Source: [artifacts/lag_spectrum_compare.json](artifacts/lag_spectrum_compare.json)

- Global peak lag: 4
- Global peak value: 0.00604422898

Target lags requested for scrutiny:

| Lag | Observed | z-score | p-value (null >= observed) | Rank in profile | Null 95% band |
|---|---:|---:|---:|---:|---|
| 5  | +0.00366221 | +3.9259 | 0.00249 | 2  | [-0.00177465, +0.00191379] |
| 6  | -0.00071979 | -0.8318 | 0.78554 | 41 | [-0.00165389, +0.00172323] |
| 12 | -0.00013880 | -0.1112 | 0.56608 | 27 | [-0.00200713, +0.00158581] |
| 13 | -0.00170671 | -1.8171 | 0.96509 | 54 | [-0.00180252, +0.00182640] |

Interpretation from these values:
- Lag 5 appears elevated in this run.
- Lags 6, 12, and 13 do not appear elevated under the current null framing.
- The strongest peak is at lag 4, not lag 13.

## Tokenization Robustness (Ambiguity and Failure Exposure)

Source: [artifacts/periodicity_robustness.json](artifacts/periodicity_robustness.json)

Word-distance target (13):
- alpha_split: z=-1.801, p=0.965, rank=37
- alpha_keep_dots: z=-1.817, p=0.968, rank=37
- alpha_collapse_runs: z=-1.966, p=0.980, rank=37
- alpha_min_len_2: z=-0.448, p=0.696, rank=26

Character lag 5:
- alpha_split: z=+4.027, p=0.00249, rank=2, null-max FPR=0.01995
- alpha_keep_dots: z=+3.985, p=0.00249, rank=2, null-max FPR=0.00998
- alpha_collapse_runs: z=+5.622, p=0.00249, rank=2, null-max FPR=0.00249
- alpha_min_len_2: z=-1.146, p=0.873, rank=40, null-max FPR=1.000

Character lag 6:
- alpha_split: z=-0.782, p=0.788, rank=41, null-max FPR=1.000
- alpha_keep_dots: z=-0.820, p=0.798, rank=41, null-max FPR=1.000
- alpha_collapse_runs: z=-3.575, p=1.000, rank=56, null-max FPR=1.000
- alpha_min_len_2: z=-1.177, p=0.890, rank=43, null-max FPR=1.000

Interpretation from robustness panel:
- The 13-word target is weak in every tokenization variant shown here.
- The lag-5 character effect is strong in three variants but fails under min-length-2 filtering.
- The lag-6 character target is not supported in this run.

## Control-Family Context

The comparative and family-aggregate spectra provide shape-level checks rather than single-value claims:
- [artifacts/plots/lag_spectra_comparative.png](artifacts/plots/lag_spectra_comparative.png)
- [artifacts/plots/lag_spectra_family_aggregate.png](artifacts/plots/lag_spectra_family_aggregate.png)
- [artifacts/plots/lag_spectra_periodogram.png](artifacts/plots/lag_spectra_periodogram.png)

What to inspect visually:
- Whether the Voynich curve is isolated or accompanied by similarly strong neighboring peaks.
- Whether spectral density shows one dominant narrow-band feature or a broader noisy field.
- Whether family curves overlap Voynich in shape and amplitude regimes.

## Current Bottom Line

What is supported by this run:
- The pipeline now exposes full empirical terrain: spectra, null histograms, confidence bands, robustness variants, and family comparison views.
- A lag-5 character anomaly appears in several variants under this specific setup.

What is not supported by this run:
- A robust lag-13 word periodicity claim.
- A robust lag-6 character periodicity claim.

Most important limitation to resolve next:
- Replace synthetic fallback transcript and repository-derived placeholder controls with canonical transcript and external historical control corpora before treating these as publication-grade inference.
