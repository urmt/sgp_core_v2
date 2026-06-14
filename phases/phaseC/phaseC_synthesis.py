"""
Phase C — Organizational Regime Discovery: Synthesis Report.
"""
print("""
╔══════════════════════════════════════════════════════════════════════╗
║     PHASE C — ORGANIZATIONAL REGIME DISCOVERY — FINAL SYNTHESIS    ║
║          5000 systems, 10 dynamical families, 5 phases              ║
╚══════════════════════════════════════════════════════════════════════╝

====================================================================
PHASE C1 — SYSTEM GENERATION
====================================================================
• 5000 systems across 10 dynamical families (500 each)
• Families: CA, oscillator, graph, population, Gray-Scott, Kuramoto,
  Lotka-Volterra, CML, replicator, branching
• 4 behavioral stability metrics + 4 fertility metrics per system
• 5 structural descriptors (CSR, RBS, ADI, RTP, SRD) per system
• Leakage audit: CSR+RBS vs all targets: max |r| = 0.255 (CLEAN)
• 2 degenerate targets (CML stability_return_time, GS stability_return_time
  — constant due to weak perturbation relative to threshold)

====================================================================
PHASE C2 — PER-DOMAIN GEOMETRY DISCOVERY
====================================================================
KEY FINDINGS:
1. ALL 10 domains have LINEAR descriptor geometry (local linearity > 0.9)
2. ALL 10 domains are DISPERSED (Hopkins > 0.5 — no clusters within domains)
3. Mean effective dimensionality: 3.8 (out of 5 descriptors, at 95% var)
4. Mean within-domain predictive R²: 0.34 (range: 0.06–0.59)
5. BEST DESCRIPTOR VARIES BY DOMAIN:
   - CSR: branching (0.17), oscillator (0.39), population (0.59)
   - RBS: CML (0.48), graph (0.58), kuramoto (0.40), replicator (0.06)
   - ADI: gray_scott (0.26), lotka_volterra (0.13)
   - RTP: cellular_automata (0.34)

No universal best descriptor. Each domain has its own geometry.

====================================================================
PHASE C3 — CROSS-DOMAIN REGIME CLASSIFICATION
====================================================================
KEY FINDINGS:
1. Weak cluster structure (max silhouette 0.208 at k=2)
2. Partition at d<4.0 yields 7 small clusters:
   - {gray_scott, oscillator}       — diffusion-reaction + oscillation
   - {LV, replicator}               — ODE cycling
   - {CML, kuramoto}                — coupled/spatial systems
   - 4 singletons: CA, graph, branching, population
3. Closest pairs: CML↔kuramoto (d=3.63), LV↔replicator (d=3.75),
   GS↔oscillator (d=3.90), osc↔pop (d=3.98)
4. Farthest pairs: branching↔CA (d=9.02)

REGIME FAMILIES IDENTIFIED:
  • BIFURCATION-FAMILY: oscillator, population, branching (CSR-dominated)
  • GRAPH-FAMILY: graph, CML, kuramoto (RBS/ADI-dominated)
  • ODE-OSCILLATOR: LV, Gray-Scott, replicator (ADI/RTP-dominated)
  • DISCRETE-SPATIAL: CA, CML (RTP/ADI)

====================================================================
PHASE C4 — REGIME TRANSITION ANALYSIS
====================================================================
KEY FINDINGS:
1. Geometry shifts WITHIN domains as system parameters change:
   - Branching LOW CSR → R²=-0.001 (no prediction)
     Branching HIGH CSR → R²=0.448 (CSR-driven, strong transition)
   - Kuramoto LOW CSR → RBS predicts (R²=0.134)
     Kuramoto HIGH CSR → ADI predicts (R²=0.357)
   - Population LOW RBS → CSR predicts (R²=0.296)
     Population HIGH RBS → SRD predicts (R²=0.659)

2. Descriptor dominance is NOT fixed within a domain
   → It depends on WHERE the system sits in parameter space

3. This explains weak cross-domain transfer:
   Different parameter regimes produce DIFFERENT geometries
   even within the SAME domain

====================================================================
PHASE C5 — FERTILITY vs STABILITY REGIMES
====================================================================
KEY FINDINGS:
1. FERTILITY is more predictable than stability in 7/10 domains
   (mean fertility R² = 0.44 vs mean stability R² = 0.26)
2. Fertility and stability R² are CORRELATED (r=0.74, p=0.015)
   → They SHARE organizational structure
3. But BEST DESCRIPTOR differs 50% of the time
   (5/10 domains use different descriptors for fertility vs stability)
4. Fertility is more predictable because it measures trajectory
   properties directly captured by descriptors (state diversity,
   transition entropy), while stability measures PERTURBATION
   RESPONSE (a more stochastic, system-specific process)

====================================================================
CROSS-PROGRAM SYNTHESIS (Phases 540–548, A, B, C)
====================================================================

  Phase 540-548: Original CLUSTER-IDENTITY-LAW → TAUTOLOGY-LAW
                  (stability_score ≡ CSR + RBS, all prior work
                   was reverse-engineering a column sum)

  Phase A:        800 systems, 4 domains, independent measures
                  → Moderate within-domain prediction (mean R²=0.49)
                  → ZERO cross-domain transfer (all R²<0)
                  → No leakage confirmed

  Phase B:        Transfer geometry across 4 domains
                  → ONE weak signal: oscillator↔population (R²≈0.5)
                  → NOT significant after null permutation tests
                  → No universal transferable structure

  Phase C:        5000 systems, 10 domains, regime discovery
                  → Each domain has ITS OWN organizational geometry
                  → No universal laws, no universal regimes
                  → CONDITIONAL REGIMES EXIST:
                    - Bifurcation systems share geometry
                    - Coupled/spatial systems share geometry
                    - ODE cycling systems share geometry
                  → Descriptor dominance shifts with system parameters
                  → Fertility more predictable than stability

====================================================================
FINAL ANSWER
====================================================================

DOES REALITY USE ONE GEOMETRY UNIVERSALLY?   → NO
ARE THERE DETECTABLE REGIME FAMILIES?        → YES (weak, conditional)
DOES DESCRIPTOR IMPORTANCE VARY?             → YES (by domain AND by
                                                 parameter regime)
IS FERTILITY DIFFERENT FROM STABILITY?       → YES (more predictable,
                                                 different descriptors)

The SFH-SGP framework identifies CONDITIONAL ORGANIZATIONAL REGIMES,
not universal laws. The structural descriptors capture real properties
of dynamical systems, but WHICH property matters depends on:
  • The dynamical family (bifurcation, network, discrete, cycling)
  • The system's position in parameter space (regime transitions)
  • The behavioral outcome (fertility vs stability)

There is no universal organizational geometry.
There are CONDITIONAL REGIMES with LOCAL TRANSFERABILITY.
""")
