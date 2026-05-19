# V2_015 REAL DATA PILOT - INIT

**Date:** 2025-05-13  
**Purpose:** Run controlled pilot testing on real sequential datasets.

**V2_015 Status:** COMPLETE - FRAMEWORK READY

## Framework Features
- Product metric (V2_013)
- Replay detection (V2_011)
- Reality threshold (calibrated to 0.12)

## Thresholds
- REALITY_THRESHOLD = 0.12 (based on V2_014: stable~0.2, random~0.07)
- REPLAY_THRESHOLD = 0.05 (from V2_011)

## Validation Results (Synthetic)
- stable_hierarchy: PASS ✓
- random_temporal: FAIL (expected) ✓
- replay_memory_spoof: FAIL (expected) ✓

## Status
**FRAMEWORK READY** - Waiting for actual real dataset to test.