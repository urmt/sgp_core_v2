# Audit: Coherence Failure Modes

**Question**: Where does coherence (C) fail to predict recovery?

**Dataset**: 60 granular DEM runs, 6 friction levels × 10 replicates, 10% removal perturbation at t=500.

---

## Failure Mode 1: Sign Ambiguity

### Description

At the same C value, the perturbation can produce OPPOSITE effects on coherence — either increasing or decreasing.

### Evidence

In the C range 0.43–0.44:
- At friction=0.40: ΔC < 0 (coherence INCREASES after removal):
  - C=0.4426, ΔC=−0.0530, rest=1.27
  - C=0.4392, ΔC=−0.0425, rest=1.29
- At friction=0.60: ΔC > 0 (coherence DECREASES after removal):
  - C=0.4333, ΔC=+0.0174, rest=1.07
- At friction=0.80: ΔC > 0:
  - C=0.4394, ΔC=+0.0696, rest=1.00
  - C=0.4306, ΔC=+0.1185, rest=0.97
  - C=0.4445, ΔC=+0.0470, rest=0.92

### Severity

Critical. C cannot predict even the DIRECTION of recovery, let alone magnitude. The sign is determined by friction (mobility regime), not by C.

### Counterargument

Maybe the sign reversal is a regime boundary effect, and C alone still works within each regime. But this defeats the claim that C universally predicts recovery — it would mean C predicts recovery only after conditioning on friction.

---

## Failure Mode 2: Recovery Speed Ambiguity

### Description

Identical C values correspond to recovery times differing by 3–4×.

### Evidence

10 matched pairs with |ΔC| ≤ 0.01 and τ_rec ratio ≥ 2:

| C | τ_rec (fast) | τ_rec (slow) | Ratio | Friction (fast) | Friction (slow) |
|---|--------------|--------------|-------|-----------------|-----------------|
| 0.486 | 37 | 137 | 3.7× | 0.10 | 0.40 |
| 0.491 | 37 | 137 | 3.7× | 0.10 | 0.40 |
| 0.471 | 37 | 112 | 3.0× | 0.10 | 0.60 |
| 0.484 | 37 | 137 | 3.7× | 0.20 | 0.40 |
| 0.482 | 37 | 137 | 3.7× | 0.20 | 0.40 |
| 0.488 | 37 | 137 | 3.7× | 0.20 | 0.40 |
| 0.466 | 37 | 112 | 3.0× | 0.20 | 0.60 |
| 0.471 | 37 | 112 | 3.0× | 0.20 | 0.60 |
| 0.490 | 37 | 137 | 3.7× | 0.20 | 0.40 |
| 0.489 | 37 | 137 | 3.7× | 0.20 | 0.40 |

### Severity

Critical. Recovery time is the most practical consequence of perturbation (fast recovery = resilient). C alone predicts essentially nothing about it (R² = 0.05).

### Pattern

All fast-recovery runs have friction ≤ 0.20 (high mobility). All slow-recovery runs have friction ≥ 0.40 (low mobility). Mobility, not C, determines recovery speed.

---

## Failure Mode 3: Within-Friction C-Tau Reversal

### Description

At every friction level where τ_rec varies, HIGHER-C runs recover MORE SLOWLY than lower-C runs — opposite of what C-alone would predict.

### Evidence

| Friction | High-C τ_rec (mean) | Low-C τ_rec (mean) | Direction |
|----------|-------------------|-------------------|-----------|
| 0.05 | 37 | 37 | Tie |
| 0.10 | 37 | 37 | Tie |
| 0.20 | 37 | 37 | Tie |
| 0.40 | 62 | 37 | **Reversed** |
| 0.60 | 82 | 52 | **Reversed** |
| 0.80 | 92 | 47 | **Reversed** |

### Severity

High. If C positively predicted recovery, higher-C systems would recover faster. At friction ≥ 0.40, the opposite occurs. The relationship flips sign.

### Interpretation

At low friction (high mobility): all systems recover fast (τ_rec = 37), so C is irrelevant to recovery time.
At high friction (low mobility): higher C means tighter packing → less free volume → slower reorganization → slower recovery.

---

## Failure Mode 4: Low C / Strong Recovery

### Description

Systems with the lowest coherence can still show excellent recovery.

### Evidence

Bottom quartile (C ≤ 0.426) runs with restoration > 1.2:

| C | ΔC | Restoration | τ_rec | Friction |
|---|----|------------|-------|----------|
| 0.4247 | −0.0743 | 1.20 | 37 | 0.40 |
| 0.3708 | −0.0017 | 1.25 | 37 | 0.60 |
| 0.4140 | +0.0537 | 1.23 | 37 | 0.60 |
| 0.3648 | −0.0282 | 1.28 | 62 | 0.80 |
| 0.3659 | +0.0159 | 1.25 | 37 | 0.80 |

### Severity

Moderate. Does not contradict "high C → good recovery" but contradicts "low C → bad recovery."

### Pattern

Low-C systems with strong recovery occur across all friction levels. The modulus of ΔC is small or negative (coherence increases or holds steady), and the system's initial low organization is not a barrier to post-perturbation reorganization.

---

## Failure Mode 5: Restoration Floor Behavior

### Description

Restoration (C_final / C_pre) shows a floor near 0.87 independent of C value.

### Evidence

The 3 worst restoration values:
- 0.8739 at C=0.4123, friction=0.80
- 0.9191 at C=0.4445, friction=0.80
- 0.9490 at C=0.4781, friction=0.40

These are all at friction ≥ 0.40. No run at friction ≤ 0.20 has restoration < 1.09.

### Severity

Low. The floor is above 0.87, meaning even the "worst" recovery restores 87% of pre-perturbation C. This may be a system-specific property (granular packing has a lower bound on disorder).

---

## Summary: What C Fails to Predict

| Property | C predicts? | Better predictor | Evidence strength |
|----------|------------|-----------------|-------------------|
| Dip direction | No | Friction | R² jump: 0.10 → 0.52 |
| Dip magnitude | Weakly | Friction + interaction | R² = 0.10 alone |
| Recovery time | No | Friction | R² jump: 0.05 → 0.35 |
| Restoration quality | Weakly | Friction + interaction | R² jump: 0.04 → 0.56 |
| Low-C bad outcome | No | 5/15 low-C cases recover well | Direct counterexample |

## What C DOES predict

| Property | C predicts? | Evidence |
|----------|------------|----------|
| High-C good outcome | Yes | All 15 high-C runs recover well (floor restoration = 1.07) |
| Structured vs unstructured | Yes | Discriminates across 8 testbeds |
| Perturbation time | Yes | Dip at perturbation is detectable at SNR = 2.14 |

## Conclusion

C is necessary but not sufficient for predicting recovery in the granular system. The two-factor model (C × mobility) is supported by every failure mode — in every case where C fails, adding friction (mobility proxy) resolves the ambiguity.

The strongest single observation: **identical C produces opposite recovery outcomes depending on friction**. This is not noise — it is a replicable, systematic pattern that C alone cannot explain.
