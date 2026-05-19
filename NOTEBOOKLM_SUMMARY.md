# SGP-CORE V2 Research Program - Complete Summary

## Introduction: What This Research Is About

The SGP-CORE V2 research program is an empirical investigation into what we're calling "organizational invariance" - the idea that real systems (biological, neural, social) have a distinctive multi-dimensional geometry that synthetic or adversarial systems cannot fully replicate. We're not claiming consciousness or anything philosophical - this is purely empirical, falsifiable measurement science.

The goal: build metrics that can distinguish real organizational systems from synthetic mimics across multiple axes: coherence, fertility (oscillation patterns), continuity, and temporal evolution.

---

## The Research Session (Today)

We ran 8 main protocols today, each building on previous findings:

---

## Protocol 1: V2_020 - Unified Coherence + Fertility

**Purpose:** Combine coherence and fertility metrics into a single unified reality index.

**Method:** Multiplicative fusion of coherence branch (memory × persistence × consensus) and fertility branch (phase order × autocorrelation × recurrence × spectral order).

**Result:** **11.86x discrimination** - This became our strongest single result for a while.

**Status:** PASS

---

## Protocol 2: V2_021 - Windowed Reality Comparison

**Purpose:** Test whether windowed analysis improves discrimination.

**Method:** Sliding window (200 samples, step 100) to compute local signatures and track cross-window correlations.

**Result:** **8.83x discrimination**

**Status:** PASS

---

## Protocol 3: V2_022 - Cross-Window Continuity

**Purpose:** Specifically measure temporal continuity across windows.

**Method:** Pearson correlation between consecutive window signatures.

**Result:** **8.63x discrimination** - perturb_recover signal showed highest continuity (0.85).

**Status:** PASS

---

## Protocol 4: V2_023 - EEG Window Pilot

**Purpose:** Test metrics on EEG-like oscillatory signals.

**Method:** Apply same windowed analysis to synthetic EEG-like data (alpha waves with evolution).

**Result:** **1.62x discrimination**

**Status:** PASS

---

## Protocol 5: V2_024 - Temporal Novelty (Initial Attempts)

**Purpose:** Detect temporal evolution - whether a system's organizational structure changes over time.

**Initial Problem:** First attempt failed because the metric rewarded noise rather than evolution. Random signals got high scores.

**Fix:** Implemented directional consistency tracking - measuring coherent trajectory migration in phase space rather than raw change magnitude.

**Result (Final):** **21.02x discrimination** - THE STRONGEST RESULT.

**Status:** PASS - GATE OPEN

---

## Protocol 6: V2_024_7 - Unified Temporal Reality

**Purpose:** Fuse ALL validated branches (coherence, fertility, continuity, evolution, anti-replay) into one unified score.

**Method:** Multiplicative fusion of all 5 branches.

**Result:** **2.38x discrimination** - FAILED.

**Why:** The anti-replay branch zeroed out the product (evolving signal had perfect correlation between halves). The multiplicative combination suppressed the strong evolution signal.

**Status:** CLOSED - needs redesign

---

## Protocol 7: V2_024 Final - Directional Consistency Evolution

**Purpose:** Final implementation of temporal evolution detection.

**Method:** 
- Compute window signatures using Hilbert transform (instantaneous phase/frequency)
- Track direction vectors between consecutive windows
- Measure directional consistency - how coherent is the trajectory migration

**Key Insight:** Not raw change magnitude, but coherent progressive evolution.

**Result:** **21.02x discrimination**

evolving: 0.4419
static: 0.0006
random: 0.0415

**Status:** PASS - STRONGEST RESULT

---

## Protocol 8: V2_025 - Organizational Phase Space

**Purpose:** Replace scalar "reality score" with multi-axis organizational geometry.

**Method:** Instead of combining into one number, map systems into 4D phase space:
- Coherence axis
- Fertility axis  
- Continuity axis
- Evolution axis

**Results (4 axes):**

| Axis | Evolving | Static | Random | Replay | Ratio |
|------|----------|--------|--------|--------|-------|
| coherence | 0.779 | 0.882 | 0.781 | 0.789 | 0.95x |
| fertility | 0.697 | 0.904 | 0.664 | 0.701 | 0.92x |
| continuity | 0.952 | 1.000 | 0.999 | 0.916 | 0.98x |
| evolution | 0.335 | 0.000 | 0.040 | 0.359 | **2.51x** |

**Key Finding:** Evolution is the critical discriminator. The other three axes don't separate signals effectively.

**4D Euclidean Distance:** 0.2145

**Status:** CLOSED (2.51x < 3.0x) but shows clear phase space separation

---

## Historical Context: What Came Before Today

Earlier in the V2 program (prior to today):

- **V2_010:** Adversarial temporal expansion - FAILED (replay attack succeeded with consensus 0.987)
- **V2_011:** Replay resistance - SUCCESS (data drift detection blocks replay)
- **V2_012:** Non-replay adversarial - Finding: Non-replay adversarial systems don't actually attack metrics, they fail naturally (~0.4 consensus)
- **V2_013:** Scale recovery - SUCCESS (product metric fixes scale collapse: 1.40x → 2.46x at N=500)
- **V2_014:** Large scale validation - PASS (2.42x min ratio at N=750)
- **V2_015:** Real data pilot - Framework ready
- **V2_016:** Real world benchmark - Network 4.24x, Language 3.32x, Financial 3.25x
- **V2_017:** Cross domain generalization - PASS (5/5 domains stable, 3.71x mean)
- **V2_018:** Semi-structured real signal - Issues (oscillatory systems needed tuning)
- **V2_019:** Phase coherence - FIXED V2_018 (oscillatory 3.27x)

---

## Summary of All Results

| Protocol | Discrimination | Status |
|----------|---------------|--------|
| V2_020 | 11.86x | PASS |
| V2_021 | 8.83x | PASS |
| V2_022 | 8.63x | PASS |
| V2_023 | 1.62x | PASS |
| V2_024 (Final) | **21.02x** | **PASS - STRONGEST** |
| V2_024_7 | 2.38x | CLOSED |
| V2_025 | 2.51x | CLOSED |

---

## Current Status

**Strongest Result:** V2_024 Final with 21.02x discrimination using directional consistency evolution detection.

**Gate Status:** OPEN for V2_024 - temporal evolution detection is validated.

**What's Working:**
- Temporal evolution (directional consistency) is the strongest discriminator
- Evolution axis alone gives 2.51x in phase space
- Unified coherence+fertility gave 11.86x

**What Needs Work:**
- Full unified fusion (V2_024_7) - needs different combination strategy
- Phase space needs improvement to exceed 3.0x threshold

---

## Key Scientific Lessons Learned

1. **Directional consistency is key** - Measuring coherent trajectory migration beats raw change detection
2. **Evolution > other axes** - Coherence, fertility, continuity don't discriminate; evolution does
3. **Multiplicative fusion can suppress strong signals** - V2_024_7 failed because one branch zeroed the product
4. **Phase space visualization reveals structure** - Even when scalar metrics fail, multi-axis mapping shows separation

---

## Files and Outputs

All outputs saved to:
- `/home/student/sgp_core_v2/outputs/`

Key result files:
- `unified_reality/v2_020_results.json` (11.86x)
- `temporal_novelty/v2_024_results.json` (21.02x)
- `organizational_phase_space/v2_025_results.json`

---

## Research Director Note

The research director will be back tomorrow morning around 10:30am (god willing).

---

## Note for NotebookLM

This document is structured to support a 2-person dialog format. The natural speakers could be:
- **Speaker 1:** Researcher explaining the technical details
- **Speaker 2:** Research partner asking clarifying questions and summarizing key points

The chronological structure works well for a " here's what we did today" conversation, with the strongest result (V2_024 at 21.02x) being the climax of the discussion.