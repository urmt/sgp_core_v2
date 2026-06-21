# RD-WELL.6C.A2 — Sparsity Injection Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** AUTHORIZED  
**Goal:** Test whether C = 0 in Acoustic Scattering is physics, measurement artifact, representation artifact, or sparsity effect.

---

## Question

Does C collapse smoothly under sparsity, or exhibit phase transitions?

---

## Background

In RD-WELL.6C.A1, C = 0 for Acoustic Scattering was observed. The sampled pressure field contains approximately 88.76% zero-valued entries.

**Hypothesis:** field sparsity may contribute to the observed C = 0.

**Status:** UNDER TEST.

This audit is now extremely important because it tests whether:

- C = 0 in Acoustic Scattering is physics
- C = 0 is measurement artifact
- C = 0 is representation artifact
- C = 0 is sparsity effect

This is exactly the kind of audit that prevents false survivors.

---

## Method

### Source Domains

Choose at least two source domains:

- Gray-Scott
- Rayleigh-Bénard

Optional:

- Active Matter

### Sparsity Levels

For each sampled field, apply artificial sparsity masks:

- 0%
- 25%
- 50%
- 75%
- 90%
- 95%
- 99%

### Masking Schemes

Use multiple masking schemes:

**Scheme A: Random masking**
- Randomly zero pixels.

**Scheme B: Spatial block masking**
- Remove contiguous regions.

**Scheme C: Threshold masking**
- Keep only top-k values.

This matters because:

> **Equal sparsity does not imply equal structure.**

---

## Measurements

For every sample compute:

- C_original
- C_sparse
- ΔC_sparse
- ΔC_rank_sparse
- fraction_zero

Also record:

- trajectory
- timepoint
- domain
- mask type
- seed

---

## Required Figures

### Figure 1: C vs sparsity

For each domain.

### Figure 2: ΔC_rank vs sparsity

### Figure 3: Compare masking schemes

No colors need special selection; default plotting is fine.

---

## Critical Question

> Does C collapse smoothly under sparsity, or exhibit phase transitions?

---

## Possible Outcomes

### Outcome A: Smooth decrease

C tracks information density.

### Outcome B: Threshold collapse

C depends on critical structure.

### Outcome C: Mask-dependent behavior

Geometry matters more than sparsity.

**Do not promote any outcome.**

---

## Explicit Warning

> **Equal sparsity does not imply equal structure.**

This may become another methodological lesson.

---

## Archive Updates

Record:

**Field Sparsity**
**PLAUSIBLE / UNDER TEST**

but only if masking actually changes C.

Otherwise:

**NOT SUPPORTED**

---

## Coupling Freeze

Keep frozen:

RD-WELL.6B coupling work

until:

- RD-WELL.6C.A2
- MHD integration
- Representation Stability Audit

complete.

---

## Status

**AUTHORIZED** — Ready to execute.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_6C_A2_SPARSITY_INJECTION_AUDIT.md`
