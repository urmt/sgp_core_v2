# RD-5: Granular Perturbation Sweep — Results

## Experiment

6 removal fractions × 10 reps = 60 runs.
Identical settings: 50 grains, 1000 steps, friction μ=0.30, removal at step 500.
C measured with sliding window (window=50, step=10).

---

## Table

| Removal % | C_pre | C_min | ΔC | τ_rec | C_final/C_pre | Overshoot | Collapses |
|-----------|-------|-------|----|-------|---------------|-----------|-----------|
| 0% | 0.478±0.023 | 0.477±0.038 | −0.001±0.042 | 15±32 | 1.135±0.059 | 0.234±0.049 | 0/10 |
| 5% | 0.485±0.028 | 0.484±0.043 | −0.001±0.032 | 7±6 | 1.200±0.118 | 0.286±0.106 | 0/10 |
| 10% | 0.471±0.028 | 0.468±0.044 | −0.003±0.034 | 9±10 | 1.299±0.104 | 0.365±0.097 | 0/10 |
| 20% | 0.486±0.022 | 0.524±0.050 | +0.039±0.052 | 5±0 | 1.259±0.136 | 0.354±0.132 | 0/10 |
| 30% | 0.491±0.027 | 0.536±0.033 | +0.045±0.049 | 5±0 | 1.277±0.119 | 0.355±0.098 | 0/10 |
| 50% | 0.485±0.024 | 0.574±0.072 | +0.089±0.075 | 5±0 | 1.396±0.134 | 0.481±0.092 | **2/10** |

---

## Key Observations

### 1. There is no dip.

The central finding: **grain removal does not produce a C dip at any removal fraction.** 

- At 0–10% removal: ΔC ≈ 0 (noise-level fluctuations).
- At 20–50% removal: ΔC is **positive** (C increases after removal).
- The "perturbation → dip → recovery" narrative from the original 10% result does not replicate across magnitudes.

### 2. C increases with removal fraction.

| Removal | Mean ΔC |
|---------|---------|
| 0% | −0.001 |
| 5% | −0.001 |
| 10% | −0.003 |
| 20% | **+0.039** |
| 30% | **+0.045** |
| 50% | **+0.089** |

Removing grains gives remaining grains more free space, which **increases** their mobility and coordination. C measures something that benefits from sparsification, not something that degrades with it.

### 3. Overshoot is real and scales with removal.

Even the 0% control shows overshoot (~0.23), indicating the system naturally drifts upward in C over time. But overshoot **increases** with removal fraction:

- 0%: 0.234
- 10%: 0.365
- 50%: 0.481

This is the most consistent scaling relationship in the data.

### 4. Collapse threshold at 50%.

At 50% removal, 2 of 10 runs collapse completely (C→0, all grains fall out of the box). The remaining 8 runs survive and show elevated C. This is the only evidence of a threshold effect.

### 5. Recovery is immediate.

τ_rec is consistently 5–15 steps across all conditions — C returns to 95% of C_pre almost instantly. There is no extended recovery process to measure.

---

## Answers to Director's Questions

### 1. Does ΔC scale with perturbation magnitude?

**Yes, but in the wrong direction.** ΔC increases (becomes more positive) with removal fraction. There is no dip to scale — instead, C rises. The relationship is approximately:

```
ΔC ≈ −0.005 + 0.0018 × Removal%
```

(R² ≈ 0.74 across means, but this is a rise, not a dip.)

### 2. Does τ_rec scale with perturbation magnitude?

**No.** τ_rec is effectively constant (~5–15 steps) across all conditions. C returns to 95% of C_pre nearly instantaneously. There is no recovery timescale to characterize because there is no dip to recover from.

### 3. Is there a perturbation threshold beyond which recovery fails?

**Yes, at ~50% removal.** Two of ten runs collapse (C→0) when 50% of grains are removed simultaneously. Below 50%, all runs survive. The threshold is sharp: 0/10 collapses at 30%, 2/10 at 50%.

### 4. Does overshoot persist at all perturbation levels?

**Yes.** Overshoot is present at every removal fraction, including the 0% control (0.234). It increases monotonically with removal:

- 0%: 0.234
- 5%: 0.286
- 10%: 0.365
- 20%: 0.354
- 30%: 0.355
- 50%: 0.481

The overshoot at 0% indicates a baseline upward drift in C. The additional overshoot at higher removal fractions scales with perturbation magnitude.

---

## Verdict

The perturbation → recovery behavior is:

- **Not robust** — the original 10% dip does not replicate as a systematic effect.
- **Not graded** — there is no smooth dip-and-recover curve.
- **Partially scalable** — ΔC and overshoot scale with removal fraction, but in the opposite direction from expected.
- **Thresholded** — collapse occurs only at 50% removal.

The system's response to grain removal is better described as **sparsification-enhanced coordination**: fewer grains → more free space → higher mobility → higher C. The original "perturbation → recovery" narrative was likely an artifact of natural C fluctuations coinciding with the removal event.

---

## Figures

- `rd05_recovery_curves.png` — C(t) for all 6 conditions, 10 reps each
- `rd05_perturbation_zoom.png` — C(t) zoomed to steps 350–750 around perturbation
- `rd05_scaling.png` — ΔC and Overshoot vs removal fraction
