# SGP-T700: Strongest Surviving Fine-Tuning Framework

## Status: CONSTRUCTION

Built from T600-surviving claims only. Every bound, dependency,
and uncertainty tracked to its source. No unverified claims.
No orphaned data. No placeholder equations.

---

## 1. Framework Scope

### What This Framework Does

Given a set of fundamental constants, determine whether the
subset of those constants constrained by carbon-based stellar
nucleosynthesis and structure formation constitutes a genuine
fine-tuning puzzle.

### What This Framework Does NOT Do

- Does NOT compute a probability (no valid measure exists)
- Does NOT assign a cause (design, multiverse, chance)
- Does NOT assume parameter independence
- Does NOT use bounds that failed T600 audit

### Output Contract

The framework produces a **constraint vector**:

\[
\mathbf{C} = \{ (\theta_i, L_i, U_i, c_i) \}
\]

where for each surviving parameter \(\theta_i\):
- \(L_i\) = lower bound for life (or ∅)
- \(U_i\) = upper bound for life (or ∅)
- \(c_i\) = confidence in the bound \{HIGH, MOD, LOW\}

The framework explicitly refuses to convert this vector into
a scalar probability.

---

## 2. Parameter Selection

### Inclusion Criteria

A parameter is included in the framework if and only if:
1. A published, peer-reviewed bound connects it to life
2. The bound survived adversarial attack in T100–T600
3. The source paper's calculations are documented

### Included Parameters

| Parameter | Symbol | Natural value | Surviving bound | Confidence | Sources |
|-----------|--------|---------------|----------------|-----------|--------|
| Cosmological constant | Λ | ~1 (Planck) | Λ < ~10⁻¹¹⁶ | HIGH | Weinberg 1987, Tegmark 2006, Barnes 2012, Piran-Jimenez 2023 |
| Strong coupling | αₛ | ~0.118 | ±1.5% for C in >15M☉ stars | MOD | Huang 2019 (MESA), Lähde 2020 (NLEFT) |
| Fine-structure constant | α | ~1/137 | ±1.5% (subdominant to αₛ) | LOW | Lähde 2020 |
| Electron-proton mass ratio | μ | 1/1836 | mₚ > mₑ (exact); factor ~100 for chemistry | LOW | Carr-Rees 1979, Adams 2019 |

### Excluded Parameters (with rationale)

| Parameter | Symbol | Reason for Exclusion | T-Source |
|-----------|--------|---------------------|----------|
| Higgs vev / Planck mass | v/M_Pl | No surviving T3 bound; Harnik (2006) weakless universe stands | T300.6A, T500.3 |
| Down-up quark mass diff | d_u | No surviving defense; NDA bounds insufficient for life claim | T300.6A, T500.3 |
| Gravitational fine-structure | α_G | Stellar structure bound only; no demonstrated life constraint | T500.5 |
| BBN αₛ bound | αₛ(BBN) | ±50% is too wide to constitute fine-tuning | T600.1 Claim 7 |

### Parameter Space Dimension

**Raw count:** 4 parameters (Λ, αₛ, α, μ)

**Effective independent degrees of freedom:** unknown
(see Section 4 — Dependency Structure)

---

## 3. Individual Bound Extraction

### 3.1 Λ: Cosmological Constant

**Bound type:** Upper (structure formation)
**Direction:** Λ must be SMALL enough for galaxies to form.

**Numerical result:**

| Source | Method | Upper bound | Notes |
|--------|--------|-------------|-------|
| Weinberg (1987) | Analytic perturbation theory | Λ < ~10⁻¹¹⁸ | First derivation |
| Tegmark et al. (2006) | N-body ΛCDM | Λ < ~10⁻¹²⁰ | 10⁶ particle simulation |
| Barnes (2012) | Analytic review | Λ < ~10⁻¹¹⁶ | Conservative composite |
| Piran-Jimenez (2023) | N-body simulation | Λ < ~10⁻¹¹⁴ | Factor ~100 variation allowed |

**Consensus bound:** Λ < 10⁻¹¹⁶ (conservative — all sources agree)
**Observed value:** Λ₀ = 10⁻¹²²

**Confidence: HIGH**
- Four independent calculations agree on existence of upper bound
- Standard gravitational physics
- No known contradiction or counterexample

**Uncertainty in bound:** ×10⁴ (factor 10⁴ between most
conservative and most stringent estimates)

**Lower bound:** NONE. Smaller Λ always produces more structure.
No minimum Λ required for life.

**Formal constraint:**

\[
\Lambda < 10^{-116} \quad \text{(galaxy formation required for life)}
\]

The condition is necessary but not sufficient for life —
galaxy formation alone does not guarantee life emerges.

---

### 3.2 αₛ: Strong Coupling Constant

**Bound type:** Two-sided (carbon production)
**Direction:** αₛ must be within a window around its observed
value for the triple-alpha process to produce sufficient carbon.

**Numerical result:**

| Source | Method | Allowed ΔE_R (Hoyle) | Implied Δαₛ/αₛ | Stellar mass range |
|--------|--------|---------------------|-----------------|-------------------|
| Livio (1989) | Stellar code (proprietary) | ±100 keV | ±0.5% | 15–40 M☉ |
| Oberhummer (2000) | Nuclear model + stellar code | ±100 keV | ±0.5% | 15–40 M☉ |
| Huang+Adams+Grohs (2019) | MESA (open source) | −300 to +500 keV | ~±1.5% | 15–40 M☉ ONLY |
| Lähde+Meißner+Epelbaum (2020) | NLEFT (lattice EFT) | Confirms Huang range | ~±1.5% | N/A (nuclear only) |

**Adopted bound (from strongest surviving source):**

Huang, Adams & Grohs (2019), *Astropart. Phys.* 105, 13.
MESA stellar evolution code. Triple-alpha reaction rate varied
via Hoyle state energy shift ΔE_R.

\[
\Delta E_R \in [-300, +500]\ \text{keV} \implies
\frac{\Delta\alpha_s}{\alpha_s} \in [-0.015, +0.025]\ \text{(approx)}
\]

Symmetrized for simplicity:

\[
\left|\frac{\Delta\alpha_s}{\alpha_s}\right| \lesssim 0.015\ \text{(±1.5%)}
\]

**Critical caveats:**
1. **Only 15–40 M☉ stars simulated.** Stars below 8 M☉ produce
   most of the carbon in the universe via AGB winds. These have
   NOT been simulated for Hoyle state sensitivity.
2. **Unreplicated.** No independent group has run this simulation.
3. **NLEFT uncertainty.** The Lähde (2020) NLEFT calculation maps
   ΔE_R to Δαₛ, but the NPLQCD vs HAL QCD controversy introduces
   systematic uncertainty in the scattering lengths.
4. **Joint α-αₛ variation not explored.** Huang varied only the
   effective nuclear force; α was held fixed.

**Confidence: MODERATE** (for ±1.5% bound in massive stars)
**LOW** (for extrapolation to all carbon production)

**Formal constraint:**

\[
\left|\frac{\alpha_s}{\alpha_{s,0}} - 1\right| < 0.015
\quad \text{(carbon production in } >15M_\odot \text{ stars)}
\]

---

### 3.3 α: Fine-Structure Constant

**Bound type:** Two-sided (carbon production, subdominant)
**Direction:** α affects triple-alpha through Coulomb barrier.

**Numerical result:**

Lähde, Meißner & Epelbaum (2020), *Eur. Phys. J. A* 56, 89:

\[
\left|\frac{\Delta\alpha}{\alpha}\right| \lesssim 0.015\ \text{(±1.5%)}
\]

This is a **subdominant** contribution. The triple-alpha rate
is ~10× more sensitive to αₛ than to α.

**Critical caveats:**
1. No independent verification.
2. Same paper as the αₛ bound — not a separate experimental check.
3. α and αₛ may be correlated in grand unified theories,
   reducing the effective number of constraints.

**Confidence: LOW**

**Formal constraint:**

\[
\left|\frac{\alpha}{\alpha_0} - 1\right| < 0.015
\quad \text{(Coulomb barrier for triple-alpha)}
\]

---

### 3.4 μ: Electron-Proton Mass Ratio

Two distinct bounds exist, at very different confidence levels.

**Bound 3.4a: mₚ > mₑ (fundamental atomic stability)**

Standard QED. If mₑ > mₚ, the electron is the heavier particle
and cannot be bound by a proton. No stable atoms.

\[
\frac{m_p}{m_e} > 1 \quad \text{(strict)}
\]

**Confidence: HIGH.** This is a QED requirement.

**Bound 3.4b: μ within factor ~100 for complex chemistry**

Carr & Rees (1979) order-of-magnitude estimate; Adams (2019) review:

\[
\mu \in [5.45 \times 10^{-5},\ 0.00545]
\]

**Critical caveats:**
1. No quantum chemistry simulation ever performed.
2. The factor ~100 is an analytic estimate.
3. This is too wide to constitute "fine-tuning" in any meaningful
   sense — a factor of 100 is not a narrow constraint.

**Confidence: LOW** (estimate only; no simulation)
**Fine-tuning relevance: NEGLIGIBLE** (too wide)

**Formal constraint (useful only):**

\[
\frac{m_p}{m_e} > 1
\]

The factor ~100 bound is excluded from quantitative analysis.

---

## 4. Dependency Structure

### 4.1 Known Correlations

| Parameter pair | Source of correlation | Strength | Framework treatment |
|---------------|---------------------|----------|--------------------|
| α — αₛ | GUT unification; common coupling at high scale | Unknown | Treat as independent (conservative); note GUT reduces DoF |
| αₛ — m_q | QCD scale Λ_QCD depends on m_q | Strong | Partially captured by NLEFT calculation |
| μ — v | Yukawa couplings in SM | Unknown | μ retained; v excluded (destroyed) |
| Λ — others | None known | None | Treat as independent (robust) |

### 4.2 The Effective Degrees of Freedom Problem

The number of INDEPENDENT parameters constrained cannot be
determined without assuming a Beyond Standard Model theory.

**Scenario analysis:**

| Scenario | Eective DoF | Rationale |
|----------|-------------|-----------|
| Minimal (all correlated in GUT) | 2 | Λ (independent) + α/αₛ/μ combined |
| Intermediate (partial correlation) | 3 | Λ + αₛ + α (or μ) |
| Maximal (all independent) | 4 | Λ + αₛ + α + μ |

**Framework position:** 2–3 effective DoF, with no way to
distinguish without a unified theory.

### 4.3 Dependency-Adjusted Constraint

If DoF = 2: Only 2 parameters (Λ and the combined αₛ/α/μ group)
must simultaneously fall in life-permitting ranges. This is
qualitatively less striking than the popular "6 DoF" claim.

If DoF = 3: Λ, αₛ, and α must simultaneously be life-permitting.
This is more constraining but still far from the standard claim.

**The framework reports the dependency structure explicitly
rather than choosing a single DoF value.**

---

## 5. Life Definition

### 5.1 Adopted Definition

This framework defines "life" as:

> **Carbon-based, information-processing, Darwinian-evolvable
> chemistry in a liquid solvent on a planetary surface.**

### 5.2 Justification

- **Carbon-based:** Petkowski, Bains & Seager (2020) provide
  MODERATE confidence that carbon is the only viable chemical
  substrate. No alternative has published chemical feasibility.
- **Information-processing:** Walker & Davies (2017) —
  information storage and replication are necessary conditions.
- **Darwinian-evolvable:** Requires heredity, variation, and
  selection. This is the only known mechanism for complex
  adaptation.
- **Liquid solvent:** Required for metabolic chemistry.
- **Planetary surface:** Required for sufficient element
  concentrations (planetesimal formation, geological cycling).

### 5.3 Sensitivity Analysis

If the definition is broadened (e.g., to include non-carbon life),
the αₛ and α constraints are weakened or destroyed.

If the definition is narrowed (e.g., requires human-like
intelligence), all bounds are unaffected (no known intelligence
constraints on fundamental constants).

**The framework notes that the αₛ/α bounds are life-definition-
dependent. The Λ bound is not.**

| Parameter | Sensitive to life definition? |
|-----------|-------------------------------|
| Λ | NO — galaxy formation is a prerequisite for any complex life |
| αₛ | YES — carbon-specific |
| α | YES — carbon-specific |
| μ | PARTIAL — general chemistry |

---

## 6. Measure Analysis

### 6.1 Framework Position

**No valid probability measure over fundamental constants has been
established.** (T600.4 — HIGH confidence.)

This framework therefore does NOT compute:

\[
P(\text{life}) = \frac{\text{volume of life-permitting region}}
{\text{volume of total parameter space}}
\]

Such a computation requires:
1. A physically justified measure μ on parameter space Ω
2. A bounded total volume ∫_Ω dμ < ∞
3. A specified life-permitting subset L ⊂ Ω

None of these requirements is satisfied.

### 6.2 What the Framework Computes Instead

The framework computes:

\[
\text{Constraint vector } \mathbf{C} = \{ (\theta_i, L_i, U_i, c_i) \}
\]

This is a geometric object: a region in parameter space that
contains all life-permitting universes, bounded by the surviving
constraints.

### 6.3 Measure-Aware Interpretation

Given \(\mathbf{C}\), different philosophical positions reach
different conclusions:

**Pro-fine-tuning interpretation:** The fact that \(\mathbf{C}\)
is a small region of the natural parameter range suggests the
universe is special.

**Skeptical interpretation:** Without a measure, "small region"
is undefined. The constraints themselves define what we can
observe; there is no independent scale to judge them against.

**This framework does not endorse either interpretation.**
It presents \(\mathbf{C}\) and lets the reader decide.

---

## 7. Observer Selection

### 7.1 Formal Statement

Observer selection (OSE) states: our observation of the constants
is conditioned on our existence. If the constants were different,
we would not exist to observe them.

\[
P(\Lambda = \Lambda_0 | \text{observers exist}) = \frac
{P(\text{observers exist} | \Lambda = \Lambda_0) \cdot P(\Lambda = \Lambda_0)}
{P(\text{observers exist})}
\]

### 7.2 Effect on the Framework

For each bounded parameter:

| Parameter | OSE explanation available? | OSE predictive power |
|-----------|---------------------------|----------------------|
| Λ < 10⁻¹¹⁶ | **YES** — we can only observe in regions with galaxies | Garriga-Vilenkin predicts Λ ≈ 7×10⁻¹¹⁹ (off by ~3000×) |
| αₛ ±1.5% | **YES** — we can only observe where carbon exists | No quantitative OSE prediction exists for αₛ |
| α ±1.5% | **YES** — we can only observe where carbon exists | No quantitative OSE prediction exists for α |

### 7.3 Remaining Tension

For Λ: The factor ~3000 discrepancy between the Garriga-Vilenkin
anthropic prediction and the observed value is unresolved. This
is mild tension for OSE but not fatal — the prediction depends
on the choice of measure (Section 6).

For αₛ: No OSE prediction exists, so no test is possible.

### 7.4 Framework Position

OSE is a complete explanation in principle for all anthropic
observations. The framework notes this but does not require it.
The framework's constraint vector \(\mathbf{C}\) is valid
regardless of whether OSE is considered the correct explanation.

---

## 8. Uncertainty Budget

### 8.1 Uncertainty Sources

| Source | Magnitude | Effect on framework |
|--------|-----------|-------------------|
| Λ bound uncertainty | ×10⁴ | Widens life-permitting region by 10⁴× |
| αₛ bound unreplicated | No independent check | ±1.5% could be larger or smaller |
| αₛ missing low-mass stars | Possibly large | If AGB stars are less sensitive, bound widens |
| NLEFT systematics | Unquantified | May shift ±1.5% to ±3% or more |
| α bound uncertainty | Same as αₛ (same paper) | Cannot be independently evaluated |
| μ bound (factor ~100) | ×100 | Too wide to contribute |
| DoF count uncertainty | 2–4 | Changes qualitative impression |
| Life definition dependence | Binary | Carbon-dependent bounds may be invalidated |

### 8.2 Propagated Constraint

Combining all uncertainties:

**Conservative (widest) life-permitting region:**

\[
\begin{aligned}
\Lambda &\in (-\infty, 10^{-116}) \\
\alpha_s &\in [\alpha_{s,0} \times 0.97, \alpha_{s,0} \times 1.03] \\
\alpha &\in [\alpha_0 \times 0.97, \alpha_0 \times 1.03] \\
m_p/m_e &> 1
\end{aligned}
\]

**Best estimate (narrowest supported by evidence):**

\[
\begin{aligned}
\Lambda &\in (-\infty, 10^{-116}) \\
\alpha_s &\in [\alpha_{s,0} \times 0.985, \alpha_{s,0} \times 1.015] \\
\alpha &\in [\alpha_0 \times 0.985, \alpha_0 \times 1.015] \\
m_p/m_e &> 1
\end{aligned}
\]

The Λ bound is one-sided (no lower bound). The αₛ bound is
two-sided but applies only to >15 M☉ stars. Extrapolation to
all carbon production is uncertain.

---

## 9. Framework Output

### 9.1 Constraint Vector

\[
\mathbf{C} = \{
    (\Lambda, -\infty, 10^{-116}, \text{HIGH}), \\
    (\alpha_s, 0.97\alpha_{s,0}, 1.03\alpha_{s,0}, \text{MOD}), \\
    (\alpha, 0.97\alpha_0, 1.03\alpha_0, \text{LOW}), \\
    (\mu, 1/1836, \infty, \text{HIGH})
\}
\]

### 9.2 What the Framework Definitively Produces

1. **Λ must be less than ~10⁻¹¹⁶** (Planck units) for galaxy
   formation. Observed Λ = 10⁻¹²² satisfies this. [HIGH confidence]

2. **αₛ must bewithin ~±1.5%** of its observed value for
   carbon production in massive stars (>15 M☉). [MOD confidence]
   Low-mass stars (dominant carbon source) have not been
   simulated. [GAP]

3. **α must be within ~±1.5%** for carbon production via
   Coulomb barrier. This is a subdominant effect. [LOW confidence]

4. **mₚ > mₑ** is required for stable atoms. [HIGH confidence]
   The narrower factor ~100 bound for complex chemistry is
   an estimate, not a simulation. [LOW confidence]

### 9.3 What the Framework Cannot Produce

- ❌ A numerical probability for life in this universe
- ❌ A statement about how "likely" or "unlikely" the constants are
- ❌ A comparison to the "natural" or "expected" values of constants
- ❌ A determination of whether the universe is or isn't fine-tuned

### 9.4 Honest Characterization

> **The evidence supports that 1–3 fundamental parameters (Λ
> definitively, αₛ probably, α possibly) are confined to
> ranges that are narrow relative to the values a naive theorist
> might consider "natural." Whether this constitutes fine-tuning
> depends on one's willingness to accept observer selection as
> an explanation and one's prior about the measure over parameter
> space. The evidence does NOT support a quantitative fine-tuning
> probability, does NOT support a multiverse, does NOT support
> design, and does NOT support the claim that fine-tuning has
> been disproven.**

### 9.5 Comparison to Standard Literature Claims

| Literature claim | This framework's assessment |
|-----------------|---------------------------|
| "The universe is fine-tuned to 1 in 10¹²⁰" | **Unsupported.** No valid measure; unjustified independence. |
| "6 parameters are independently fine-tuned" | **False.** 2–4 survive audit; only Λ is robust. |
| "αₛ is fine-tuned to ±0.5%" | **Overstated.** Modern bound is ±1.5%. Unreplicated. |
| "The Hoyle state is fine-tuned to 1%" | **Conditionally defensible** as sensitivity statement. Not a probability. |
| "Fine-tuning is an illusion" | **Unsupported.** The constraints exist; their interpretation is debated. |
| "OSE explains everything" | **Unsupported for αₛ.** No quantitative OSE prediction exists. |

---

## 10. Limits of the Framework

### 10.1 What Would Change the Output

| Discovery | Effect |
|-----------|--------|
| Independent MESA replication of αₛ bounds (including low-mass stars) | Raises αₛ confidence to MOD-HIGH |
| Alternative biochemistry demonstration | Destroys αₛ and α bounds |
| Valid measure from fundamental theory | Enables probability computation |
| Non-anthropic Λ explanation | Destroys Λ as FT evidence |
| Simulation of μ showing narrower bound | Adds μ as constrained parameter |

### 10.2 What Would Not Change the Output

- Additional probability calculations using current assumptions
- New variants of the standard anthropic argument
- Speculation about string theory landscapes
- Philosophical arguments about design or chance

---

## Appendix A: Source Papers and Audit Status

| Paper | Role | Audited in | Status |
|-------|------|-----------|--------|
| Weinberg (1987) | Λ upper bound | T200, T300 | Survives |
| Tegmark et al. (2006) | Λ N-body bound | T200, T300 | Survives |
| Barnes (2012) | Λ review | T200, T300, T500 | Survives |
| Piran-Jimenez (2023) | Λ N-body bound | T600.2 | Survives |
| Garriga-Vilenkin (2003) | OSE for Λ | T400, T600 | Survives (qualified) |
| Huang+Adams+Grohs (2019) | MESA triple-alpha | T600.2 | Adopted (widest bound) |
| Lähde+Meißner+Epelbaum (2020) | NLEFT triple-alpha | T600.2 | Adopted (bound map) |
| Petkowski+Bains+Seager (2020) | Silicon life refutation | T600.3 | Adopted (life definition) |
| Livio et al. (1989) | Original Hoyle FT | T200, T300, T500 | Superseded (unreplicated) |
| Oberhummer et al. (2000) | Original Hoyle FT | T200, T300, T500 | Superseded (not independent) |
| Bains (2004) | Silicon life proposal | T500, T600.3 | Superseded by Petkowski 2020 |
| Harnik (2006) | Weakless universe | T300.6A, T500 | Destroys v/M_Pl |

## Appendix B: The Framework in 50 Words

The cosmological constant must be small enough for galaxies
(HIGH confidence). The strong coupling must be within ~±1.5%
for carbon in massive stars (MOD confidence). That's the core.
No probability can be computed. Observer selection explains
at least the Λ observation. Whether this constitutes
fine-tuning is a question of interpretation, not measurement.

---

## Appendix C: Live Verification Record

| Check | Status | Date |
|-------|--------|------|
| All bounds sourced to published papers | ✓ | 2026-06-03 |
| No SFH code or orphaned datasets | ✓ | 2026-06-03 |
| No unverified probability calculations | ✓ | 2026-06-03 |
| Uncertainty sources documented | ✓ | 2026-06-03 |
| Dependency structure explicit | ✓ | 2026-06-03 |
| Life definition stated and justified | ✓ | 2026-06-03 |
| Measure problem documented | ✓ | 2026-06-03 |
| Framework limitations stated | ✓ | 2026-06-03 |
| Does not exceed what T600 supports | ✓ | 2026-06-03 |
