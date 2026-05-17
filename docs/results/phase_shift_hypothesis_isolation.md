# Phase-Shift Hypothesis Isolation (Completed Testing Phase)

## Purpose

This note evaluates competing explanations for observed early-vs-late differences in Voynich section structure.

Question tested:
- Does a two-phase production model explain the data better than a single uniform process?
- If yes, which signal is strongest: lag-6 magnitude shift or global profile regularization shift?

Current defensible statement:

The Voynich Manuscript exhibits constrained procedural behavior, positional dependence, and nonrandom geometric structure that are more consistent with an engineered hybrid artifact than with conventional high-information semantic encoding systems, while specific mechanism identity and authorship remain open.

## Data and Setup

Inputs:
- `data/takahashi_eva.txt`
- `artifacts/section_lag_spectrum_compare_min800.json`

Consolidated test output:
- `artifacts/phase_shift_test_min800_v2.json`

Section rule:
- Keep sections with at least 800 alpha characters.
- Retained sections: 65.

Metrics:
- `lag6`: lag-6 autocorrelation excess over unigram expectation.
- `rough`: standard deviation of section lag profile across lags 1..60 (higher = less regular).
- `peak`: lag of maximum autocorrelation excess.

Important correction:
- Earlier drafts undercounted sections because strict tag parsing excluded forms like `101r1`.
- Final results here use corrected section parsing and all 65 retained sections.

## Final Early-vs-Late Quartile Results (65 Sections)

From `phase_shift_test_min800_v2.json`:

- `sections_used = 65`, `quartile_window = 16`
- Early average lag6: `0.024458`
- Late average lag6: `0.038095`
- Late-minus-early lag6 difference: `+0.013637`, permutation `p = 0.019596`
- Early peak-at-lag6 share: `0.3125`
- Late peak-at-lag6 share: `0.8125`

- Early average roughness: `0.015117`
- Late average roughness: `0.013873`
- Late-minus-early roughness difference: `-0.001244`, permutation `p = 0.108778`

Interpretation:
- On this finalized 65-section set, lag-6 separation between early and late windows is statistically supported.
- Roughness is directionally lower in later folios but not significant under quartile-window mean comparison.

## Robustness Cuts

### Outlier-trimmed (remove one high and one low lag6 section per side)
- `n_early = 14`, `n_late = 14`
- Lag6 difference: `+0.012657`, `p = 0.013997`
- Roughness difference: `-0.001271`, `p = 0.092477`

### Size-balanced (late sections constrained to early section char range)
- `n_early = 12`, `n_late = 12`, `char_range = [801, 2721]`
- Lag6 difference: `+0.013657`, `p = 0.051487`
- Roughness difference: `-0.001527`, `p = 0.100225`

Interpretation:
- Lag6 shift remains positive under all cuts; strongest support appears in base and trimmed settings.
- Size-balancing weakens lag6 significance to borderline levels.
- Roughness remains directionally lower later but is not robustly significant in these mean-difference tests.

## Single-Changepoint Scan

Weighted one-breakpoint model versus one-phase baseline:

For `lag6`:
- Best split: `after 107r / before 107v`
- Gain: `3.154117`
- Permutation `p = 0.136288` (not significant)

For `rough`:
- Best split: `after 111r / before 111v`
- Gain: `0.096856`
- Permutation `p = 0.018327` (significant)

Top combined normalized split candidates (lag6 + rough):
- `after 84v / before 85r1` (combined `0.173525`)
- `after 111v / before 112r` (combined `0.161869`)
- `after 111r / before 111v` (combined `0.161533`)

Interpretation:
- A roughness-oriented structural transition near `111r/111v` remains statistically credible.
- A pure lag6 changepoint is not yet significant in the one-breakpoint permutation test.

## Cause Isolation (Most Likely to Less Likely)

Most supported:
1. Heterogeneous production process with at least one late regularization shift.
2. Early-vs-late separation in lag-6 concentration, likely coupled to section/function changes.

Plausible but unresolved:
3. Different operator/template settings across phases.
4. Topic/genre mix changes that alter repetitive structure without mechanism change.

Less supported as sole explanation:
5. Pure random partition artifact.
6. Pure outlier artifact.
7. Pure length artifact.

## Updated Working Model

Current best model is phased hybrid production:
- Earlier region: lower lag6 concentration and less constrained structure.
- Later region: substantially higher lag6 concentration and stronger regularization signatures.

This does not require a strict binary claim of "handwritten" versus "stenciled". It supports process heterogeneity.

## What Is Not Yet Proven

- Direct mechanism identity for the phase shift.
- A single universally dominant breakpoint for all metrics.
- Section-level semantic translatability of early folios.

## Status

This testing phase is complete for the current transcript and section threshold (`min_section_chars = 800`).
The repository now has a consolidated artifact-level summary suitable for hypothesis readjustment and preregistration of next-round tests.
