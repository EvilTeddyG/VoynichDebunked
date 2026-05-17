# Comparative Audit: Voynich vs. Constrained Synthetic Model
## Beinecke MS 408 and a Markov/Template Generator (Evidence-Oriented View)

This document compares observed Voynich metrics with one constrained synthetic generator class. The goal is not to claim identity of mechanism, but to evaluate whether a low-state procedural model can reproduce multiple anomaly signals simultaneously.

---

## 1. Metric Snapshot

| Metric | Voynich (Observed) | Synthetic (One Run) | Interpretation Scope |
|---|---:|---:|---|
| Character entropy H0 | 3.9534 | 3.7429 | Similar alphabet-distribution complexity range |
| Conditional entropy H1 | 2.3102 | 2.1633 | Both in low-uncertainty regime |
| Vertical column matches | 7.00% | 7.15% | Similar elevated alignment rate |
| Dominant phrase spacing signal | 13-word peak present | 13-word peak present | Candidate periodicity overlap |

Notes:
1. Similarity in summary metrics does not imply unique causation.
2. Metrics should be interpreted with control-family and null-model context.

---

## 2. What This Comparison Supports

The side-by-side comparison supports an existence claim:

A constrained procedural generator can produce outputs in the same anomaly region as Voynichese for entropy, positional effects, and periodicity-related signals.

That is evidence of model plausibility, not exclusive proof.

---

## 3. What This Comparison Does Not Establish

This file alone does not establish:

1. That the specific generator implementation is historically correct.
2. That one exact stencil geometry is uniquely identified.
3. That semantic-language or cipher alternatives are globally impossible.
4. That historical production provenance is proven from simulation metrics.

---

## 4. Where This Audit Is Most Informative

This comparison is most informative when read together with:

1. Class-aware controls: [control_family_benchmark.py](control_family_benchmark.py)
2. Significance and null tests: [significance_tests.py](significance_tests.py)
3. Periodicity robustness stress tests: [periodicity_robustness.py](periodicity_robustness.py)
4. Hold-out predictive checks: [cross_validate_markov.py](cross_validate_markov.py)

The strongest inference is convergence under independent checks, not any single table row.

---

## 5. Practical Reading Rule

Use this document as a comparative exhibit, not a standalone verdict.

If synthetic and observed metrics are close, that is sufficient to keep the procedural-generation family in play. Stronger claims require additional evidence from control-family separation, null-calibrated spectra, and held-out generalization behavior.
