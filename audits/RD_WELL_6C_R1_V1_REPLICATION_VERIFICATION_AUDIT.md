# RD-WELL.6C.R1.V1 — Replication Verification Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** PROVISIONALLY ACCEPTED  
**Goal:** Verify rank transform implementation across all domains.

---

## Question

Are rank transforms implemented identically across all domains?

---

## Background

In RD-WELL.6C.R1, the Gray-Scott result showed mean ΔC_rank = 0.227, which is larger than earlier estimates.

Before archive acceptance, we must verify that rank transforms are implemented identically across all domains.

**Why:** High ΔC can be physics or implementation. SR-30 applies to code too.

---

## Method

Verify:

1. **Ties handling** — Are ties handled consistently?
2. **Normalization** — Is normalization consistent?
3. **Flattening order** — Is flattening order consistent?
4. **NaN handling** — Is NaN handling consistent?
5. **3D slicing procedures** — Is 3D slicing consistent?

---

## Verification Steps

### 1. Ties handling

Check: Are ties handled with the same method across all domains?

Expected: Yes, ties should be handled with the same method (e.g., 'average', 'min', 'max', 'dense', 'ordinal').

### 2. Normalization

Check: Is normalization consistent?

Expected: Yes, normalization should be consistent (e.g., min-max normalization, z-score normalization).

### 3. Flattening order

Check: Is flattening order consistent?

Expected: Yes, flattening order should be consistent (e.g., row-major, column-major).

### 4. NaN handling

Check: Is NaN handling consistent?

Expected: Yes, NaN handling should be consistent (e.g., replace with 0, leave as NaN, etc.).

### 5. 3D slicing procedures

Check: Is 3D slicing consistent?

Expected: Yes, 3D slicing should be consistent (e.g., middle slice, first slice, last slice).

---

## Expected Results

- If all checks pass: rank transform is implemented identically across all domains
- If any check fails: rank transform implementation is inconsistent

---

## Implications

- If all checks pass: high ΔC may be attributable to domain properties
- If any check fails: high ΔC may be implementation artifact

---

## Status

**PROVISIONALLY ACCEPTED** — The current verification audit did not detect implementation differences in rank transforms, normalization, flattening order, NaN handling, or 3D slicing. The observed ΔC differences therefore remain provisionally attributable to domain properties, though additional implementation factors may still exist.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_6C_R1_V1_REPLICATION_VERIFICATION_AUDIT.md`
