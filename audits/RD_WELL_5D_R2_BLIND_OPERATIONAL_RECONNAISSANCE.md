# RD-WELL.5D.R2 — Blind Operational Reconnaissance

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Describe before explain"  
**Status:** COMPLETE

---

## Method

Like RD-WELL.2: describe only appearance, disappearance, repetition, stabilization, boundary formation, movement.

Forbidden: coherence, organization, emergence, complexity, information, adaptation.

No metrics. No C. No stabilization. Only operational description.

---

## Rayleigh-Bénard

### Buoyancy

| Quantity | Value |
|----------|-------|
| Mean | 0.1460 |
| Std | 0.1995 |
| Min | 0.0000 |
| Max | 0.9989 |
| Frame-to-frame change | 0.0068 |
| Gradient magnitude | 0.0072 |

**Appearance over time:**
- t=0: mean=0.1000, std=0.0707
- t=1: mean=0.1351, std=0.1785
- t=2: mean=0.1420, std=0.1924
- t=3: mean=0.1465, std=0.2005
- t=4: mean=0.1499, std=0.2065

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

### Pressure

| Quantity | Value |
|----------|-------|
| Mean | -0.0042 |
| Std | 0.0355 |
| Min | -0.0800 |
| Max | 0.0335 |
| Frame-to-frame change | 0.0037 |
| Gradient magnitude | 0.0008 |

**Appearance over time:**
- t=0: mean=0.0000, std=0.0000
- t=1: mean=-0.0043, std=0.0367
- t=2: mean=-0.0044, std=0.0370
- t=3: mean=-0.0045, std=0.0371
- t=4: mean=-0.0046, std=0.0373

**Boundary formation:**
- t=0: top=0.0000, bottom=0.0000, left=0.0000, right=0.0000
- t=1: top=-0.0043, bottom=-0.0043, left=-0.0700, right=0.0334
- t=2: top=-0.0044, bottom=-0.0044, left=-0.0719, right=0.0334

---

### Velocity Magnitude

| Quantity | Value |
|----------|-------|
| Mean | 0.0000 |
| Std | 0.0000 |
| Min | 0.0000 |
| Max | 0.0002 |
| Frame-to-frame change | 0.0000 |
| Gradient magnitude | 0.0000 |

**Appearance over time:**
- t=0: mean=0.0000, std=0.0000
- t=1: mean=0.0000, std=0.0000
- t=2: mean=0.0000, std=0.0000
- t=3: mean=0.0000, std=0.0000
- t=4: mean=0.0000, std=0.0000

---

## Active Matter

### Concentration

| Quantity | Value |
|----------|-------|
| Mean | 1.0000 |
| Std | 0.0068 |
| Min | 0.9633 |
| Max | 1.0406 |
| Frame-to-frame change | 0.0009 |
| Gradient magnitude | 0.0008 |

**Appearance over time:**
- t=0: mean=1.0000, std=0.0115
- t=1: mean=1.0000, std=0.0090
- t=2: mean=1.0000, std=0.0075
- t=3: mean=1.0000, std=0.0066
- t=4: mean=1.0000, std=0.0060

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

### Velocity Magnitude

| Quantity | Value |
|----------|-------|
| Mean | 0.0008 |
| Std | 0.0004 |
| Min | 0.0000 |
| Max | 0.0027 |
| Frame-to-frame change | 0.0000 |
| Gradient magnitude | 0.0001 |

**Appearance over time:**
- t=0: mean=0.0010, std=0.0005
- t=1: mean=0.0009, std=0.0004
- t=2: mean=0.0009, std=0.0004
- t=3: mean=0.0008, std=0.0004
- t=4: mean=0.0008, std=0.0004

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

## Status

Operational reconnaissance complete. No analysis performed.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r2/blind_operational_reconnaissance.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r2/run_blind_operational_reconnaissance.py`
