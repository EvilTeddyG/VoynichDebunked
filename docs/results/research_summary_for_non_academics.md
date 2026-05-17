# Research Summary for Non-Academics

## Plain-Language Abstract

This project asks a simple question: is the Voynich Manuscript more likely to be a hidden normal language, or a text produced by a constrained writing process?

Using reproducible measurements on the manuscript transcript, the current results lean toward the second option. The writing behaves less like normal language and more like output from a strict production system with repeated patterns and line-layout constraints.

This is not a claim that every mystery is solved. It is a claim that a mechanical-generation explanation currently fits key measurable features better than a straightforward natural-language decipherment model.

## What We Did

- Measured how predictable character sequences are in Voynich text.
- Measured where words and glyph patterns appear within lines.
- Compared Voynich patterns to external baseline corpora.
- Ran permutation and robustness tests to check whether key patterns survive perturbations.
- Built a synthetic generator to test whether a constrained process can reproduce the same anomaly profile.

## Key Outcomes (In Plain Terms)

1. Voynich text is unusually predictable at the character-transition level.
2. Several strong spacing and lag signals appear in the full text profile.
3. A constrained generation model can reproduce major parts of the anomaly pattern.
4. Some periodicity claims are sensitive to preprocessing choices, so not every apparent pattern is equally stable.
5. The evidence currently supports a strong process-level hypothesis, not a solved translation.

## What This Does Not Claim

- It does not identify an author.
- It does not provide a full readable plaintext translation.
- It does not prove historical motive.
- It does not close every alternative explanation.

## Why This Matters

Most Voynich debates focus on one dramatic decode claim. This project instead provides a transparent, testable framework that other researchers can rerun, challenge, and improve. Even if parts of the hypothesis change, the reproducible method and open artifact trail remain useful.

## Current Bottom Line

The manuscript is still mysterious, but the balance of evidence in this repository currently favors constrained generation behavior over ordinary hidden-language behavior. The responsible interpretation is: strong, reproducible signal of structured artificiality, with some components still requiring broader controls and stricter cross-checking.

## Next Steps for Stronger Confidence

- Expand and rebalance control corpora.
- Align robustness and preprocessing definitions under one shared policy.
- Increase section-level coverage so more folio groups are tested at sufficient sample size.
- Keep claim boundaries conservative and evidence-traceable.
