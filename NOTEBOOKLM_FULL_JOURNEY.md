# SGP Complete Research Journey - For Audio Overview

## The Story: Two Projects, One Journey

This research spans two projects:
- **SGP-Tribe3 (V1)**: Neural network observability and organizational invariants
- **sgp_core_v2 (V2)**: Temporal geometry for time-series classification

Both ask: **Can we find universal patterns in complex signals?**

---

## Part 1: V1 - The Neural Network Quest (115 experiments)

### What We Started With
We wanted to find "organizational invariants" — patterns that appear regardless of the specific neural network architecture or dataset.

### The Journey
1. **Early phases (10-15)**: Training dynamics, spectral analysis, manifold geometry
2. **Information geometry (66-70)**: Using probability space shapes to analyze networks
3. **Observer theory (71-76)**: Can networks understand themselves?
4. **Falsification program (83-100)**: Putting our claims to the test
5. **Real data (101-115)**: Finding actual EEG data and validating

### The Hard Truth
- Cross-domain invariants? **NOT FOUND**
- Causal temporal patterns? **DESTROYED** by controls
- Universality claims? **MOSTLY REDUCIBLE** to simple linear stats
- Synthetic artifacts? All gone when tested on real data

### The Unexpected Twist
When we finally got real EEG data (5 subjects from CHB-MIT dataset):
- **Robust structure emerged** — AUC = 1.0 on cross-subject validation
- **Phase sensitivity confirmed** — AUC = 0.783 on hierarchical surrogates

The signal was real after all — just hiding behind overly strict controls.

---

## Part 2: V2 - The Temporal Geometry Pivot (35+ experiments)

### The Problem Discovered
We had a time-series classification system that was failing. Not because the data was confusing — but because the decision method was broken.

### The Key Findings

**F001: The embeddings are actually good**
- 80% accuracy using simple nearest-neighbor
- (Random would be 20%)
- The information was always there

**F002: The gate was destroying information**
- Original "gate" system: 30% accuracy on regime_switch
- Switching to LDA classifier: 90% accuracy
- Same data, completely different results

**F003: Replay is always 100%**
- The "replay" transformation duplicates the first half
- This creates a consistent pattern the metrics catch
- Perfect separation, every time, on every signal type

**F004: Random walk has irreducible overlap**
- Stochastic signals have genuine ambiguity
- Different random walks can look similar
- Separation ratio only 2.15 — not enough for perfect classification

**F005: The manifold is one-dimensional**
- 99.3% of variance in just one direction
- Four metrics, but they mostly measure the same thing
- Adding more metrics would give diminishing returns

### The Five Postulates (P1-P5)

1. **Effective 1D Manifold**: Embeddings collapse to nearly one dimension
2. **Orthogonal Encoding**: Metrics capture partially independent properties
3. **Gate Destruction**: Simple thresholds discard recoverable information
4. **Replay Invariance**: Temporal duplication preserves certain metrics
5. **Stochastic Irreducibility**: Some overlap is fundamental, not fixable

---

## The Bottom Line

### V1 Takeaway
Real neural data contains robust temporal organization — but only if you use the right validation. Synthetic patterns mostly didn't survive real-world testing.

### V2 Takeaway
The bottleneck wasn't the data — it was the classifier. Simple threshold gates throw away information that sophisticated classifiers can use. But some limits are real: stochastic signals have irreducible overlap.

### Connection Between Projects
Both projects found the same thing: **what you measure matters as much as how you measure it**. The right validation (V1) or the right classifier (V2) reveals structure that naive methods miss.

---

## Quick Reference: Experiments by Numbers

| Project | Range | Count |
|---------|-------|-------|
| V1 Phases | 10-115 | 115 |
| V2 Versions | V2_004-V2_082 | ~25 |
| V2 Validation | A01-A06 | 6 |
| V2 Theory | T001-T012 | 12 |
| **TOTAL** | — | **~158** |

---

## Key Datasets

**V1**: CHB-MIT EEG (5 subjects, 2,105 windows)

**V2**: V2_079 Canonical
- 10 random seeds
- 5 signal types (chirp, rw_trend, regime_switch, chaotic_logistic, coupled_osc)
- 5 transformations (base, reverse, swap, replay, stitch)
- 4 metrics per signal

---

*Generated May 2026*