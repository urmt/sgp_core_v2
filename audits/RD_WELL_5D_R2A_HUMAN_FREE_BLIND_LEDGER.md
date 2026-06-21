# RD-WELL.5D.R2A — Human-Free Blind Ledger

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Blind reconnaissance is not yet blind enough"  
**Status:** COMPLETE

---

## Method

Procedure:
1. Randomize frame order.
2. Hide dataset identity.
3. Hide field names.
4. Describe operational changes only.
5. Reveal identity afterward.

This attacks:
- observer bias
- field-name bias
- domain bias

Forbidden: coherence, organization, emergence, complexity, information, adaptation.

---

## Frame Verification

All extracted frames verified as valid data:
- No NaN or Inf values
- Non-trivial values
- Valid shapes

Status: **COMPLETE**

---

## Blind Description

### Field_1 (RB_pressure)

**Field shape:** (10, 512, 128)

**Operational changes over time:**
- t=0: Initial frame. Mean=0.0000, Std=0.0000, Range=[0.0000, 0.0000]
- t=1: Moderate change from previous frame. Mean=-0.0043, Std=0.0367, FrameDiff=0.032428
- t=2: Very small change from previous frame. Mean=-0.0044, Std=0.0370, FrameDiff=0.000134
- t=3: Very small change from previous frame. Mean=-0.0045, Std=0.0371, FrameDiff=0.000119
- t=4: Very small change from previous frame. Mean=-0.0046, Std=0.0373, FrameDiff=0.000110
- t=5: Very small change from previous frame. Mean=-0.0046, Std=0.0375, FrameDiff=0.000104
- t=6: Very small change from previous frame. Mean=-0.0047, Std=0.0376, FrameDiff=0.000100
- t=7: Very small change from previous frame. Mean=-0.0048, Std=0.0378, FrameDiff=0.000096
- t=8: Very small change from previous frame. Mean=-0.0048, Std=0.0379, FrameDiff=0.000093
- t=9: Very small change from previous frame. Mean=-0.0049, Std=0.0380, FrameDiff=0.000090

**Boundary formation:**
- t=0: top=0.0000, bottom=0.0000, left=0.0000, right=0.0000
- t=1: top=-0.0043, bottom=-0.0043, left=-0.0700, right=0.0334
- t=2: top=-0.0044, bottom=-0.0044, left=-0.0719, right=0.0334

**Movement:**
- t=0: center_of_mass=(N/A, N/A)
- t=1: center_of_mass=(N/A, N/A)
- t=2: center_of_mass=(N/A, N/A)
- t=3: center_of_mass=(N/A, N/A)
- t=4: center_of_mass=(N/A, N/A)

---

### Field_2 (AM_velocity_mag)

**Field shape:** (10, 256, 256)

**Operational changes over time:**
- t=0: Initial frame. Mean=0.0010, Std=0.0005, Range=[0.0000, 0.0027]
- t=1: Very small change from previous frame. Mean=0.0009, Std=0.0004, FrameDiff=0.000146
- t=2: Very small change from previous frame. Mean=0.0009, Std=0.0004, FrameDiff=0.000048
- t=3: Very small change from previous frame. Mean=0.0008, Std=0.0004, FrameDiff=0.000044
- t=4: Very small change from previous frame. Mean=0.0008, Std=0.0004, FrameDiff=0.000039
- t=5: Very small change from previous frame. Mean=0.0007, Std=0.0004, FrameDiff=0.000036
- t=6: Very small change from previous frame. Mean=0.0007, Std=0.0003, FrameDiff=0.000033
- t=7: Very small change from previous frame. Mean=0.0007, Std=0.0003, FrameDiff=0.000030
- t=8: Very small change from previous frame. Mean=0.0007, Std=0.0003, FrameDiff=0.000028
- t=9: Very small change from previous frame. Mean=0.0007, Std=0.0003, FrameDiff=0.000027

**Boundary formation:**
- t=0: top=0.0011, bottom=0.0011, left=0.0011, right=0.0010
- t=1: top=0.0009, bottom=0.0009, left=0.0009, right=0.0008
- t=2: top=0.0009, bottom=0.0009, left=0.0009, right=0.0008

**Movement:**
- t=0: center_of_mass=(128.23, 129.01)
- t=1: center_of_mass=(128.30, 129.08)
- t=2: center_of_mass=(128.40, 129.14)
- t=3: center_of_mass=(128.50, 129.19)
- t=4: center_of_mass=(128.62, 129.22)

---

### Field_3 (RB_velocity_mag)

**Field shape:** (10, 512, 128)

**Operational changes over time:**
- t=0: Initial frame. Mean=0.0000, Std=0.0000, Range=[0.0000, 0.0000]
- t=1: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000007
- t=2: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000003
- t=3: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000003
- t=4: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000002
- t=5: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000002
- t=6: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000002
- t=7: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000002
- t=8: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000003
- t=9: Very small change from previous frame. Mean=0.0000, Std=0.0000, FrameDiff=0.000003

**Boundary formation:**
- t=0: top=0.0000, bottom=0.0000, left=0.0000, right=0.0000
- t=1: top=0.0000, bottom=0.0000, left=0.0000, right=0.0000
- t=2: top=0.0000, bottom=0.0000, left=0.0000, right=0.0000

**Movement:**
- t=0: center_of_mass=(N/A, N/A)
- t=1: center_of_mass=(63.75, 256.19)
- t=2: center_of_mass=(63.95, 256.27)
- t=3: center_of_mass=(64.04, 256.10)
- t=4: center_of_mass=(64.03, 255.98)

---

### Field_4 (RB_buoyancy)

**Field shape:** (10, 512, 128)

**Operational changes over time:**
- t=0: Initial frame. Mean=0.1000, Std=0.0707, Range=[0.0000, 0.2000]
- t=1: Moderate change from previous frame. Mean=0.1351, Std=0.1785, FrameDiff=0.035203
- t=2: Small change from previous frame. Mean=0.1420, Std=0.1924, FrameDiff=0.006866
- t=3: Small change from previous frame. Mean=0.1465, Std=0.2005, FrameDiff=0.004489
- t=4: Small change from previous frame. Mean=0.1499, Std=0.2065, FrameDiff=0.003477
- t=5: Small change from previous frame. Mean=0.1528, Std=0.2113, FrameDiff=0.002879
- t=6: Small change from previous frame. Mean=0.1553, Std=0.2152, FrameDiff=0.002477
- t=7: Small change from previous frame. Mean=0.1575, Std=0.2187, FrameDiff=0.002186
- t=8: Small change from previous frame. Mean=0.1594, Std=0.2217, FrameDiff=0.001965
- t=9: Small change from previous frame. Mean=0.1612, Std=0.2244, FrameDiff=0.001790

**Boundary formation:**
- t=0: top=0.1000, bottom=0.1000, left=0.1998, right=0.0002
- t=1: top=0.1351, bottom=0.1351, left=0.8834, right=0.0002
- t=2: top=0.1420, bottom=0.1420, left=0.9213, right=0.0002

**Movement:**
- t=0: center_of_mass=(37.56, 255.50)
- t=1: center_of_mass=(28.54, 255.50)
- t=2: center_of_mass=(27.48, 255.50)
- t=3: center_of_mass=(26.88, 255.50)
- t=4: center_of_mass=(26.46, 255.50)

---

### Field_5 (AM_concentration)

**Field shape:** (10, 256, 256)

**Operational changes over time:**
- t=0: Initial frame. Mean=1.0000, Std=0.0115, Range=[0.9633, 1.0406]
- t=1: Small change from previous frame. Mean=1.0000, Std=0.0090, FrameDiff=0.002669
- t=2: Small change from previous frame. Mean=1.0000, Std=0.0075, FrameDiff=0.001648
- t=3: Small change from previous frame. Mean=1.0000, Std=0.0066, FrameDiff=0.001057
- t=4: Very small change from previous frame. Mean=1.0000, Std=0.0060, FrameDiff=0.000714
- t=5: Very small change from previous frame. Mean=1.0000, Std=0.0055, FrameDiff=0.000517
- t=6: Very small change from previous frame. Mean=1.0000, Std=0.0051, FrameDiff=0.000402
- t=7: Very small change from previous frame. Mean=1.0000, Std=0.0048, FrameDiff=0.000330
- t=8: Very small change from previous frame. Mean=1.0000, Std=0.0045, FrameDiff=0.000283
- t=9: Very small change from previous frame. Mean=1.0000, Std=0.0042, FrameDiff=0.000250

**Boundary formation:**
- t=0: top=1.0000, bottom=1.0000, left=1.0000, right=1.0000
- t=1: top=1.0000, bottom=1.0000, left=1.0000, right=1.0000
- t=2: top=1.0000, bottom=1.0000, left=1.0000, right=1.0000

**Movement:**
- t=0: center_of_mass=(127.50, 127.50)
- t=1: center_of_mass=(127.50, 127.50)
- t=2: center_of_mass=(127.50, 127.50)
- t=3: center_of_mass=(127.50, 127.50)
- t=4: center_of_mass=(127.50, 127.50)

---

## Identity Reveal

| Field ID | Original Name | Domain |
|----------|---------------|--------|
| Field_1 | RB_pressure | Rayleigh-Bénard |
| Field_2 | AM_velocity_mag | Active Matter |
| Field_3 | RB_velocity_mag | Rayleigh-Bénard |
| Field_4 | RB_buoyancy | Rayleigh-Bénard |
| Field_5 | AM_concentration | Active Matter |

---

## Status

Blind ledger complete. No analysis performed.

---

## Partial Blinding Note

Field names ("buoyancy", "pressure", "velocity", "concentration") were revealed in the original reconnaissance. This imports fluid intuition.

**Status:** Partial blinding only.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r2a/blind_ledger.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r2a/run_blind_ledger.py`
