# REALITY GATE V5 - TEMPORAL ADVERSARIAL TESTING

**Date:** 2025-05-13  
**Status:** CLOSED - FAIL

## Gate Criteria
| Criteria | Target | Result | Status |
|----------|--------|--------|--------|
| Classifier accuracy | >80% | 68% | FAIL |
| False positive rate | <15% | 33% | FAIL |
| Multi-seed stable | CV<0.15 | 0.039 | PASS |
| Scale robustness | survives | FAIL | FAIL |
| Adversarial spoofing | mostly fail | FAIL | FAIL |

## Summary
**GATE CLOSED** - Temporal metrics FAILED adversarial testing.

## Key Vulnerabilities
1. **Replay attack succeeded completely** - replay_memory_spoof achieved consensus=0.987 (highest of all systems)
2. **Scale collapse** - discrimination drops from 1.40x at N=50 to 1.08x at N=250
3. **Classifier failed** - 68% accuracy, 33% FPR

## What Survived
- Multi-seed stability (CV < 0.15 for stable_hierarchy)
- Recovery ratio discrimination (stable 1.32x vs random 0.96x)

## Recommendations
- Reject temporal memory claims until metrics are redesigned
- Add memory-consistency checks (memory ≈ consensus)
- Require adversarial resistance before real-data testing