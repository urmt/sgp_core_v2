"""
Phase B Synthesis — Transfer Geometry Program.
"""
print("""
╔══════════════════════════════════════════════════════════════════════╗
║    SFH-SGP TRANSFER GEOMETRY — FINAL SYNTHESIS (Phases B1–B6)      ║
║           800 systems, 4 domains, 6 targets, 4 model types           ║
╚══════════════════════════════════════════════════════════════════════╝

====================================================================
SUMMARY OF FINDINGS
====================================================================

1. PAIRWISE TRANSFER MATRIX (B1)
   -------------------------------
   Within-domain:   mean R² = 0.73 ± 0.29
   Cross-domain:    mean R² = NEGATIVE (no universal transfer)

   After domain-standardizing targets to remove scale effects:
   Cross-domain (aligned): mean ≈ -1.6, range [-5.2, +0.62]
   Positive cross-domain rate: 12.5% (9/72 pair×target combinations)

   THE ONLY CONSISTENT POSITIVE TRANSFER:
   nonlinear_oscillator → population
     - fertility_state_diversity:       R² = 0.537, r = 0.734
     - fertility_transition_entropy:    R² = 0.526, r = 0.738
     - stability_return_time:           R² = 0.398, r = 0.650
     - stability_recovery_rate:         R² = 0.156, r = 0.420
   
   This is an ASYMMETRIC transfer (osc→pop >> pop→osc).

2. UNIVERSALITY CLUSTERING (B2)
   ----------------------------
   All 4 domains form separate clusters at D < 0.5.
   Closest pair: oscillator - population (distance = 0.97).
   Hierarchical clustering confirms NO universality classes exist.
   Each domain is its own predictive "island."

3. REPRESENTATION ALIGNMENT (B3)
   ----------------------------
   CCA shows weak canonical correlations (max 0.33 for CA-pop).
   Aligned latent spaces do NOT recover transferability.
   The descriptor→outcome mappings are fundamentally domain-specific.

4. FEATURE STABILITY (B4)
   ----------------------------
   Feature importance is ENTIRELY domain-dependent:
     - CA:      RTP dominates (transition entropy)
     - Graph:   CSR + SRD dominate (graph complexity + size)
     - Osc:     CSR dominates (nonlinearity strength)
     - Pop:     CSR dominates (trajectory entropy)
   Cross-domain coefficient correlations are OFTEN NEGATIVE,
   confirming that different descriptors predict the SAME
   behavioral outcome with OPPOSITE weight across domains.

5. NULL UNIVERSE TESTS (B5)
   ----------------------------
   After standardization correction, the oscillator→population
   transfer survives but is WEAK (positive only for some targets).
   Global null: NOT SIGNIFICANT (p ≈ 1.0 for raw R², improvement
   with standardized targets but still dominated by negative pairs).
   Pair (osc-pop): nominal significance for fertility metrics.

6. META-PREDICTIVE GEOMETRY (B6)
   ----------------------------
   Property space distance does NOT predict transfer success
   (r between property distance and transfer: undefined/nan).
   The 4 domains are too few and too different for meta-analysis.

====================================================================
ANSWER TO THE CENTRAL QUESTION
====================================================================

Do transferable universality classes exist?
-------------------------------------------

YES — ONE WEAK SIGNAL:
   nonlinear_oscillator → population transfers at R² ≈ 0.5
   for fertility-related targets (state diversity, transition entropy).

NO — EVERYWHERE ELSE:
   All other cross-domain pairs show NEGATIVE transfer.
   CCA, Procrustes, and domain adaptation cannot recover it.
   Universal rules do NOT exist.

CONDITIONAL STRUCTURE:
   The oscillator↔population connection is INCOMPLETE:
     - Directional (osc→pop works, pop→osc is weaker)
     - Target-dependent (fertility: yes, stability: weak)
     - Not robust to representation alignment (CCA fails)

====================================================================
WHY OSCILLATOR → POPULATION TRANSFERS (PARTIALLY)
====================================================================

Both are 1D / 2D bifurcation-controlled dynamical systems:

  Duffing oscillator:  x'' + δx' + αx + βx³ = γcos(ωt)
  Logistic map:        x_{n+1} = rx_n(1 - x_n)

Both have:
  - A control parameter determining dynamical regime
    (osc: β, δ, γ / pop: r)
  - A continuous state space (osc: phase plane / pop: population)
  - Bifurcation structure (osc: nonlinear stiffness / pop: Feigenbaum)
  - State diversity that increases with nonlinearity

The structural descriptors capture these shared properties:
  - CSR (nonlinearity strength) → predicts fertility state diversity
  - ADI (autocorrelation) → reflects periodic/chaotic regime

CA and graph diffusion lack this parameterized bifurcation structure:
  - CA: discrete rule table, no continuous bifurcation
  - Graph: fixed topology, no parametric regime control

====================================================================
CONCLUSION
====================================================================

The SFH-SGP structural descriptors (CSR, RBS, ADI, RTP, SRD)
have VALID WITHIN-DOMAIN predictive power but FAIL as universal
descriptors. The only detectable transferability is between
dynamical systems that share continuous bifurcation structure
(oscillators ↔ population dynamics).

This is NOT a law.
This is a CONDITIONAL STRUCTURAL TENDENCY.
It applies only within specific dynamical families and only
for specific behavioral outcomes.

RECOMMENDATION:
  - Do NOT search for universal predictive laws
  - DO characterize per-domain descriptor-outcome profiles
  - DO test whether descriptor OPERATIONALIZATION can be unified
  - DO investigate the oscillator-population connection with
    a broader family of bifurcation-based dynamical systems
""")
