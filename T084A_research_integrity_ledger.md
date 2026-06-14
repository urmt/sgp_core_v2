# T084A — Research Integrity Ledger

**Directive:** No new mechanisms, constraints, or theories introduced. Evidence validation and chain-of-reasoning verification only.

**Audit Scope:** T075 through T083 (stability/fertility tradeoff → latent geometry of generative models).

---

## Pre-Audit: Data Quality Revelation

**Critical finding before any claim verification:** All 30 configurations in T075, T076, T077, and T078 are **hand-scored estimates** by the experimenter on 10 subjective axes (0.00–1.00), not empirical measurements. The same data appears in T078's PCA, T075's correlation, T076's geometry, T077's attractor analysis.

| File | Data Source |
|------|------------|
| `T075_stability_fertility_tradeoff.py` lines 28–136 | Hand-scored DOMAIN_DATA |
| `T076_boundary_geometry_audit.py` (same block) | Same hand-scored DOMAIN_DATA |
| `T077_attractor_audit.py` (same block) | Same hand-scored DOMAIN_DATA |
| `T078_meta_space_reconstruction.py` lines 25–136 | Same hand-scored DOMAIN_DATA |
| `T081_constraint_generativity_audit.py` | Independent Markov chain simulation |
| `T082_structural_realization_audit.py` | Independent Markov chain simulation |
| `T083_latent_geometry_audit.py` | Based on T082's Markov chain framework |

**Impact:** T075–T078 form a closed loop — same hand-assigned scores feed into correlation analysis, PCA, boundary geometry, and attractor classification. These are not four independent lines of evidence converging; they are four transformations of a single subjective dataset.

---

## Full Claim Inventory

### Claim 1: Stability and fertility are negatively coupled within the viable region (r = -0.331)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T075 |
| **Exact measurement(s)** | Global r = +0.271; viable-only r = -0.331 |
| **Analysis** | Correlation flips sign when non-viable systems are excluded — the sign change comes from excluding low-stability, low-fertility collapsed systems. This is a Simpson's paradox pattern: the global relationship is driven by non-viable systems dragging both tails down. The viable-only negative correlation is a second-order effect dependent on which systems are labeled "viable" (which thresholds were set in T073). |
| **Alternative explanations not ruled out** | (a) Simpson's paradox artifact of threshold choice; (b) scoring bias (did the scorer unconsciously assign fertile systems lower stability?); (c) the 20 viable configurations are insufficient for stable correlation estimation (r = -0.331, p ≈ 0.15 with N=20). |
| **Confidence** | **Low** — single audit, hand-scored data, small N, sign-flip pattern, threshold-dependent |
| **Methodological flags** | ⚠ Correlation treated as causation. ⚠ Single audit. ⚠ Simpson's paradox not tested. ⚠ No confidence interval or significance test reported. |

---

### Claim 2: Maximum fertility occurs at intermediate stability (0.72), not at maximum stability

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T075 |
| **Exact measurement(s)** | System with max fertility (0.94) has stability 0.717 |
| **Analysis** | This is a single data point — the "Super-fertile universe (hypothetical)" configuration. Its stability score of 0.717 was hand-assigned. The claim that "maximum fertility occurs at intermediate stability" extrapolates from one hand-scored hypothetical point. Additionally, ZFC set theory (stability 0.80, fertility 0.87) and Computation/Turing (stability 0.80, fertility 0.85) have higher stability with fertility scores within 0.07–0.09 of the max — consistent with a plateau, not a peaked relationship. |
| **Alternative explanations not ruled out** | (a) Fertility plateau (not a peak) — no significant difference between stability 0.72 and 0.80 fertile systems; (b) floor/celling artifact — extreme stability values (0.95+) may be rare in the scoring scheme by construction; (c) single-point dependence. |
| **Confidence** | **Low** — depends on a single hand-scored hypothetical data point. The "at 0.72" precision is unwarranted. |
| **Methodological flags** | ⚠ Single audit. ⚠ Single data point claim. ⚠ Precision unjustified by data. |

---

### Claim 3: Three-zone landscape (collapse → fertile corridor → fortress) exists in ALL domains

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T076 |
| **Exact measurement(s)** | All 4 domains show viability → fertility → fortress zones |
| **Analysis** | The three zones are a logical consequence of how the data was constructed: systems were pre-labeled as viable/fertile and then their stability values were examined. In any dataset where viability requires intermediate scores on C/P/G/R/S and fertility requires high SR/NP/RC/RD/OE, a three-zone pattern in the stability dimension is entailed by the scoring criteria. This is not an empirical discovery — it is a restatement of the definition. The "fortress" label (high stability, low fertility) applies to systems like Presburger arithmetic and FOL decidable fragments — but these are viable by definition (they meet the viability thresholds). The program determined they were "not fertile" and labeled their high-stability cluster "fortress." |
| **Alternative explanations not ruled out** | (a) Trivially true by construction — if fertile systems are defined as high on fertility axes and viable systems as intermediate on stability axes, then unstable → viable → fortress is a definitional artifact; (b) the "collapse" zone includes systems that are not actually dynamical collapses but simply uninteresting by design (e.g., thermal equilibrium is assigned G=0.05 by fiat). |
| **Confidence** | **Moderate** — the three-zone structure is real but its interpretation as a "landscape" with "collapse" and "fortress" boundaries is metaphorical. The actual shape depends entirely on how viability/fertility thresholds were drawn. |
| **Methodological flags** | ⚠ PCA geometry treated as ontology (implicitly: the latent space is claimed to be "real," not a projection). ⚠ Results may be definitional rather than empirical. |

---

### Claim 4: Corridor widths cluster near 0.05–0.10 across all domains

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T076 |
| **Exact measurement(s)** | Domain A: 0.05, Domain B: 0.05, Domain C: 0.084, Domain D: 0.10 |
| **Analysis** | Corridor width is measured in the stability dimension (derived from C+P+R/3). The 0.05–0.10 range means "fertile systems in each domain occupy a narrow band of stability values." With only 2–4 fertile systems per domain, the width is determined by the difference between the highest and lowest stability values among those 2–4 hand-scored systems. With N=2, the "width" is just the distance between two hand-assigned numbers. |
| **Alternative explanations not ruled out** | (a) Measurement artifact of small N — with 2 data points, corridor width has no statistical meaning; (b) the scorer may have implicitly kept fertile systems at similar stability levels when assigning scores; (c) different definitions of "width" would give different values. |
| **Confidence** | **Low** — N=2-4 fertile systems per domain, hand-scored data. The "0.05–0.10 clustering" finding appears robust in pattern but not in precision. |
| **Methodological flags** | ⚠ Single audit. ⚠ Small-N precision overclaimed. ⚠ Hand-scored data amplification. |

---

### Claim 5: Fertile corridor is NOT a universal attractor (3/4 domains are Saddles, 1/4 is Transit)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T077 |
| **Exact measurement(s)** | Domain A: Type III Transit, Domain B/C/D: Type II Saddle; retention strengths 0.496–1.627; recovery potentials 0–0.238; basin fill ratios 0.272–1.0 |
| **Analysis** | The attractor classification depends on retention, recovery, and basin fill — quantities computed from the hand-scored data and a nearest-neighbor perturbation model within that data. The "perturbation" test examines what happens when a system's stability value shifts, using linear interpolation of scores. This tests behavior within a model of the data, not actual dynamical behavior of real systems. The claim that "the corridor persists even when attractors do not" is a property of the interpolation model, not a dynamical systems finding. |
| **Alternative explanations not ruled out** | (a) The modeled dynamics are a linear interpolation of hand-scored data, not actual dynamical evolution; (b) recovery potential of 0 in 2 domains may reflect limited data (no fertile neighbors in scoring space), not genuine non-recoverability; (c) classification may be sensitive to arbitrary parameters of the perturbation model (step size, boundary definitions). |
| **Confidence** | **Low** — the attractor analysis models dynamics where none were measured. The corridor persistence claim is a feature of the interpolation model. |
| **Methodological flags** | ⚠ Single audit. ⚠ Simulation results generalized beyond tested conditions — results from an interpolation model on hand-scored data are treated as dynamical systems findings. |

---

### Claim 6: 10 metrics compress to 2 latent dimensions (92.6% variance); PC1 = 75.1%

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T078 |
| **Exact measurement(s)** | PC1 = 75.14%, PC2 = 17.48%, PC3 = 3.11%; Kaiser criterion = 0; elbow = 2 |
| **Analysis** | Kaiser criterion finding 0 components > eigenvalue 1.0 is a red flag — it means no single PC explains more variance than one original variable. This often indicates that the data has no genuine low-dimensional structure. The 75.1% PC1 is high because the 30 hand-scored configurations were constructed with correlated scores (e.g., fertile systems have high SR, NP, RC, RD, OE simultaneously by design — the scorer assigned them together). These correlations are built into the data by the scoring methodology, not discovered in it. With N=30 and M=10, PCA can produce spurious structure: the ratio is barely above the 3:1 minimum recommended for stable PCA. |
| **Alternative explanations not ruled out** | (a) The PC1 = 75.1% reflects construction artifact — the scorer implicitly correlated generative variables across fertile systems; (b) Kaiser = 0 means the PCA may be detecting noise; (c) with N=30, the eigenvalue estimates have wide confidence intervals; (d) T083 independently confirmed that no generative model can reproduce this geometry (max PC1 = 51.6%), suggesting the T078 geometry is an artifact of the hand-scoring procedure. |
| **Confidence** | **Low** — N=30, M=10, Kaiser = 0, the geometry could not be reproduced by T083's generative models. The T083 result (51.6% max) is arguably the more trustworthy estimate because it comes from a simulated generative process, not hand-scored data. |
| **Methodological flags** | ⚠ PCA geometry treated as ontology (the latent dimensions are given interpretive labels as if they are real axes). ⚠ Results from hand-scored data treated as measurement. ⚠ T083's failure to reproduce is evidence against the T078 geometry being real. |

---

### Claim 7: PC1 = Generative Capacity, PC2 = Structural Stability (interpretive labels)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T078 (eigenvector interpretation) |
| **Exact measurement(s)** | PC1 positive: SR(+0.39), NP(+0.38), G(+0.36), OE(+0.33), RC(+0.32); PC2 positive: R(+0.60), P(+0.42), C(+0.40); PC2 negative: G(-0.28), S(-0.26) |
| **Analysis** | These are interpretations of eigenvector loadings, not measurements. The labels "Generative Capacity" and "Structural Stability" are the experimenter's suggested interpretations. PC1 loads on ALL variables positively (likely a size component — "overall system richness"). PC2 shows a contrast between coherence/structure (R, P, C) and generativity/novelty (G, S negatively loaded). The "generative capacity" label for PC1 is reasonable as a description but claiming it as a discovered latent dimension is over-interpretation. |
| **Alternative explanations not ruled out** | (a) PC1 may be a "size" or "overall activity" component, not specifically generative capacity; (b) the loadings are heavily influenced by which variables the scorer chose to correlate; (c) different variable scalings or normalizations would change the interpretation. |
| **Confidence** | **Moderate** for the observation that fertile systems score high on multiple correlated axes (trivially true given scoring). **Low** for the claim that these are discovered universal latent dimensions. |
| **Methodological flags** | ⚠ PCA geometry treated as ontology. ⚠ Interpretive labels given without validation (e.g., no independent test that PC1 measures "generativity" rather than "overall activity"). |

---

### Claim 8: Fertile corridor is a single connected region in latent space (spread 0.289)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T078 |
| **Exact measurement(s)** | 12 fertile systems; cluster spread = 0.289; max deviation = 0.544 |
| **Analysis** | With 12 fertile systems in a 3D latent space, "connected" is not statistically meaningful — 12 points can always be called a cluster if drawn from any distribution that is not multimodal. The spread of 0.289 relative to the max deviation of 0.544 means some fertile points are nearly twice as far from centroid as the average — suggesting elongation or outliers, not a tight cluster. |
| **Alternative explanations not ruled out** | (a) Any 12 points drawn from a unimodal distribution would show similar "connectivity"; (b) the 12 fertile points are non-randomly distributed across the domain structure (4 from domain A, 4 from B, 2 from C, 2 from D) — the "connectedness" may reflect the domain grouping, not a universal corridor; (c) the connectedness claim depends on the specific 3D projection, which was chosen post-hoc. |
| **Confidence** | **Low** — the "connected corridor" claim is not statistically tested. Any set of 12 points in 3D with spread 0.289 could be called "connected" by this criterion. |
| **Methodological flags** | ⚠ Simulation results generalized beyond tested conditions. ⚠ Single audit. ⚠ No null model comparison (what spread would random points show?). |

---

### Claim 9: MC3 (Constraint Balance) is the highest-ranked meta-constraint (+22/32 findings)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T079 |
| **Exact measurement(s)** | MC3: +22, coverage 22/32 (68.75%), robustness 1.0 |
| **Analysis** | The T079 scoring is a hand-assigned table: the experimenter judged each of 32 findings against each of 5 meta-constraints as +1 (predicts), 0 (neutral), or -1 (contradicts). There is no independent or blinded procedure. The same person who formulated the meta-constraints also scored them against their own findings. MC3 scores +22 because the experimenter found it consistent with 22 findings — but this is a consistency check, not a predictive test. The "robustness 1.0" means no contradictions were found, which may reflect either genuine compatibility or selective attention. |
| **Alternative explanations not ruled out** | (a) Confirmation bias — the scorer may unconsciously favor their own constructs; (b) MC3 is vague enough to be consistent with many findings (Constraint Balance can explain almost any intermediate outcome); (c) no inter-rater reliability or blinded scoring was performed. |
| **Confidence** | **Low** — subjective scoring by the same person who formulated the constraints. The core idea (balance matters) is plausible but the +22 numerical score has no objective basis. |
| **Methodological flags** | ⚠ Correlation treated as causation (MC3 is consistent with findings, not proven to generate them). ⚠ Single audit. ⚠ No independence between constraint formulation and constraint scoring. |

---

### Claim 10: MC2 + MC3 generate 8/9 substrate assumptions; MC4 adds EC1 (NEAR-COMPLETE EMERGENCE)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T080 |
| **Exact measurement(s)** | MC2+MC3 coverage: 8/9 assumptions; MC4 adds EC1; direction test: 3.6 vs 2.0 |
| **Analysis** | The prediction scores in T080's mapping table are the same kind of hand-assigned +1/0/-1 as T079. The "direction test" compares "average assumption predicts MCs" (2.0) vs "average MC predicts assumptions" (3.6). But these are not independent measures: the experimenter assigns both scores. A meta-constraint could "predict" more assumptions simply because it was formulated more broadly. The 3.6 vs 2.0 difference may reflect that MCs are broader concepts than assumptions, not a genuine dependency direction. |
| **Alternative explanations not ruled out** | (a) The direction test measures concept breadth, not dependency direction; (b) no alternative mapping was tested (e.g., what if a different person scored the table?); (c) T081's generative simulation FAILED to reproduce this emergence pattern (only 2/9 assumptions emerged) — meaning the claimed "emergence" from T080 does not work when actually simulated. T082 then required adding a new principle (SP/MC5/MC1) to make emergence work — suggesting the T080 claim was premature. |
| **Confidence** | **Low** — the generative tests (T081, T082) contradict the claim. T080's "emergence" is a conceptual mapping, not an operational demonstration. When actually simulated, MC2+MC3+MC4 alone do NOT generate the substrate. |
| **Methodological flags** | ⚠ Correlation treated as causation. ⚠ Single audit (and subsequently contradicted by T081). ⚠ Subjective scoring without validation. |

---

### Claim 11: T081 failed because of missing stability counterpressure (SP/MC5/MC1)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T081, T082 |
| **Exact measurement(s)** | Baseline: 5/9 assumptions, 1/8 mechanisms emerged; +SP: 9/9 assumptions, 5/8 mechanisms |
| **Analysis** | T082 showed that adding Structural Persistence (SP), MC5, or MC1 to the baseline MC2+MC3+MC4 causes full assumption emergence. This is a genuine generative simulation result — it's not hand-scored, it's a Markov chain model output. However, the interpretation that "SP is the missing element" depends on: (a) whether SP is genuinely distinct from the meta-constraints or a re-description of MC5/MC1; (b) whether the simulation model is correctly specified (are the parameter ranges calibrated? does the Markov chain capture the right dynamics?); (c) whether any of SP, MC5, or MC1 is the "correct" missing element or simply any stability-promoting term. |
| **Alternative explanations not ruled out** | (a) The generative model may be under-specified — adding almost any structure-promoting term would "fix" emergence; (b) SP, MC5, and MC1 may not be distinct — their similar effects suggest they may be different formulations of the same underlying principle; (c) the model may have parametric freedom to produce any desired outcome by tuning. |
| **Confidence** | **Moderate** for the experimental result (adding a stability term changes assumption emergence). **Low** for the claim that SP is the specific missing element — MC5 and MC1 worked equally well. |
| **Methodological flags** | ⚠ Single audit (two audits run on the same simulation framework). ⚠ No test of whether the simulation is calibrated to behave like real systems. |

---

### Claim 12: Substrate generation ≠ viability generation (experimentally separated in T082)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T082 ablation: MC3 removed → 9/9 assumptions, viability collapses; SP removed → 5/9 assumptions, viability persists |
| **Exact measurement(s)** | -MC3: 9 assumptions, no viability; -SP: 5 assumptions, viability; -MC2: 3 assumptions, viability; -MC4: 9 assumptions, viability |
| **Analysis** | This ablation experiment is a genuine result from the generative simulation. The finding that removing MC3 preserves all 9 assumptions but destroys viability, while removing SP preserves viability but destroys assumption emergence, demonstrates functional dissociation. This is the strongest finding in the T081-T083 chain because it uses computational ablation (independent mechanism) rather than subjective scoring. |
| **Alternative explanations not ruled out** | (a) The dissociation may be an artifact of the specific Markov chain architecture — different generative models might not show the same separation; (b) "viability" in the simulation is defined by the same thresholds used in T073, which may not translate across modeling frameworks. |
| **Confidence** | **Moderate-High** for the result that assumption generation and viability generation are dissociable in this simulation architecture. **Low** for the claim that this is a universal property of real systems. |
| **Methodological flags** | ⚠ Simulation results generalized beyond tested conditions (the dissociation is demonstrated in one simulation framework). |

---

### Claim 13: T078's latent geometry (PC1=75.1%) is a cross-domain ensemble property, not locally generable

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T083 |
| **Exact measurement(s)** | Best PC1 = 51.6% (Combined), all phases ≤ 51.6%, intrinsic dim = 3-4 |
| **Analysis** | This is a genuine negative result from a computational experiment. However, the interpretation is speculative. The claim that "it must be a cross-domain ensemble property" is one possible explanation. Alternative: the T078 geometry is an artifact of hand-scored data (correlated scoring) and therefore cannot be reproduced by any model that generates data from first principles. The T083 result is consistent with BOTH explanations: (a) geometry is a cross-domain ensemble property, OR (b) the original T078 geometry was never real to begin with. The audit chose interpretation (a). |
| **Alternative explanations not ruled out** | (a) The T078 geometry is an artifact of hand-scoring (correlated variable assignment), not a real property — T083's failure to reproduce it supports this at least as strongly as the ensemble property interpretation; (b) the generative model in T083 may lack the right mechanism — not because the mechanism is "cross-domain" but because the experimenter didn't try the right generative process; (c) cross-domain variance would need to be explicitly tested (T084 proposal) before this interpretation is warranted. |
| **Confidence** | **High** for the negative experimental result (PC1 ≤ 51.6% in all conditions). **Low** for the interpretation that the gap is due to cross-domain ensemble properties. |
| **Methodological flags** | ⚠ Simulation results generalized beyond tested conditions (the "cross-domain ensemble" explanation goes beyond what T083 tested). ⚠ Alternative (b) — T078 artifact — is equally consistent with the evidence but was deprioritized in interpretation. |

---

### Claim 14: Viability constraints are ABOVE the substrate, not beneath it (three-layer architecture)

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T073, T080 |
| **Exact measurement(s)** | Viability threshold (C≥0.75, P≥0.65, G≥0.40, R≥0.30, S≥0.10) derived from domain configurations |
| **Analysis** | This claim originated in T073's finding that viability constraints can discriminate viable from non-viable systems without reference to substrate assumptions. T080's emergence finding supports it conceptually. However, the viability thresholds were derived from the same 30 hand-scored configurations — they are empirical regularities in the scoring data, not independently measured properties. The claim that viability sits "above" the substrate is a logical conclusion from the data organization (viability is a property of outcomes, not assumptions) but the specific threshold values are data-dependent. |
| **Alternative explanations not ruled out** | (a) Viability thresholds are specific to the 30 hand-scored examples — different configurations would give different thresholds; (b) the "above substrate" claim is logical but not empirically tested — no test was done where substrate assumptions vary independently and viability is measured as outcome. |
| **Confidence** | **Moderate** for the architectural claim (viability is outcome-level, not assumption-level). **Low** for the specific threshold values (0.75, 0.65, 0.40, 0.30, 0.10). |
| **Methodological flags** | ⚠ Single audit-derived thresholds. ⚠ No cross-validation on held-out configurations. |

---

### Claim 15: 5/6 failure classes are universal; only F4 (runaway divergence) is contingent

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T072, T072b |
| **Exact measurement(s)** | F1-F3, F5-F6 found across all 4 domains; F4 domain-contingent |
| **Analysis** | The failure classes were derived from T072's analysis of 8 failure modes × 4 domains, clustered into F1-F6. This is one of the more robust analyses in the chain because it examines actual failure patterns across domains rather than assigning numerical scores. However, the "universality" claim is limited by the same 4-domain dataset — claiming 5/6 are universal from 4 examples is weak evidence. |
| **Alternative explanations not ruled out** | (a) With only 4 domains, "universal" means "present in all 4 tested" — adding more domains could reveal contingency; (b) F4's "contingency" might reflect incomplete domain sampling rather than genuine domain-specificity. |
| **Confidence** | **Moderate** — the failure class taxonomy is well-grounded but "universality" is overclaimed from N=4. |
| **Methodological flags** | ⚠ "Universal" overclaimed from 4 examples. |

---

### Claim 16: Minimal constraint set (MC2+MC3+MC4) is the deepest layer; substrate is derived, not fundamental

| Field | Content |
|-------|---------|
| **Supporting audit(s)** | T079, T080 |
| **Exact measurement(s)** | MC2+MC3+MC4 covers all 32 findings; T080 "NEAR-COMPLETE EMERGENCE" |
| **Analysis** | This is the program's central philosophical claim. It depends on the chain: T079 (MC3+MC2+MC4 covers findings) → T080 (MCs predict assumptions) → "substrate is derived." But T081 showed the MCs alone cannot GENERATE the substrate (only MC3+MC2+MC4 in simulation gave 5/9 assumptions). T082 then required adding SP/MC5/MC1 to achieve full generation. If SP/MC5/MC1 are required for generative sufficiency, then the "minimal set" is actually MC2+MC3+MC4+SP/MC5/MC1 — at minimum 4 constraints, not 3. Calling 3 constraints "the deepest layer" while a 4th is needed to make it work is a tension in the claims. |
| **Alternative explanations not ruled out** | (a) The minimal set may be larger than claimed (SP or MC5 or MC1 required for generation); (b) the MCs may not be "deeper" than the substrate but simply broader generalizations of the same ideas; (c) T080's emergence claim and T081/T082's generative failure are in direct tension — the claim privileges T080's conceptual mapping over T081/T082's computational demonstration. |
| **Confidence** | **Low** — T081/T082 experimentally undermine the central claim. The generative simulation requires an additional principle (SP/MC5/MC1) that was not part of the original minimal set. |
| **Methodological flags** | ⚠ Single audit for the central claim (T080), contradicted by subsequent generative tests (T081). ⚠ Correlation treated as causation (conceptual "prediction" confused with generative production). |

---

## Summary: Methodological Flaw Inventory

| # | Issue | Affected Claims |
|---|-------|-----------------|
| 1 | **Hand-scored data treated as measurement** — All 30 configurations are subjective estimates, not empirical observations | Claims 1, 2, 3, 4, 5, 6, 7, 8, 14 |
| 2 | **Closed-loop data** — T075-T078 use the same DOMAIN_DATA block, not independent evidence | Claims 1, 2, 3, 4, 5, 6, 7, 8 |
| 3 | **Subjective mapping without blinding** — +1/0/-1 scores assigned by the same person who formulated both the constraints and the findings | Claims 9, 10 |
| 4 | **Correlation → causation** — "Predicts" in T079/T080 means "is consistent with," not "generates" | Claims 9, 10, 13, 16 |
| 5 | **PCA geometry → ontology** — Interpretive labels applied to latent dimensions as if discovered | Claims 6, 7 |
| 6 | **Small-N overclaiming of precision** — Corridor width to 2 decimal places from N=2-4 fertile systems per domain | Claim 4 |
| 7 | **Simulation → reality** — Markov chain results generalized to claims about real systems | Claims 5, 11, 12, 13 |
| 8 | **"Universal" from N=4** — 4 domains is insufficient to establish universality | Claim 15 |
| 9 | **Contradiction between conceptual and generative evidence** — T080 claims emergence that T081/T082 cannot reproduce | Claims 10, 16 |
| 10 | **Interpretation favored over equally consistent alternative** — T083 geometry gap explained as "cross-domain ensemble" without testing or acknowledging the artifact interpretation | Claim 13 |

---

## Three-Class Classification

### ESTABLISHED FINDINGS (warranted by the evidence)

| # | Finding | Basis | Confidence |
|---|---------|-------|------------|
| E1 | The 9-assumption substrate has a bootstrap dependency structure centered on OC2, with an over-asserted IS1→IS2 edge that causes deadlock | T056–T069 formal dependency analysis (graph-theoretic, not hand-scored) | **High** |
| E2 | 8 mechanism classes compress from 70 candidates (8.75:1 ratio) | T059 compression audit on explicit enumeration | **High** |
| E3 | Viability can be characterized by 5 axes with threshold constraints that discriminate viable from non-viable | T073 computed from domain data (but threshold values depend on that data) | **Moderate** |
| E4 | Fertile vs merely-viable separation is achievable with a signature emphasizing RC as the best discriminator | T074 computed from domain data | **Moderate** |
| E5 | Failure mode taxonomy (F1–F6) with 2 universal categories (generativity loss, fragmentation) and 1 contingent category (runaway divergence) | T072, T072b cross-domain failure analysis | **Moderate** |
| E6 | Substrate assumption generation and viability generation are functionally dissociable in a Markov chain simulation (T082 ablation) | T082 computational experiment | **Moderate** |
| E7 | MC2+MC3+MC4 + SP/MC5/MC1 generates all 9 substrate assumptions and 5/8 mechanisms in the T082 simulation | T082 generative simulation | **Moderate** |
| E8 | The T078 latent geometry (PC1=75.1%) cannot be reproduced by single-regime generative models (max PC1=51.6%) | T083 negative experimental result | **High** |

### TENTATIVE FINDINGS (plausible but insufficiently tested)

| # | Finding | Uncertainty | Key Gap |
|---|---------|-------------|---------|
| T1 | Stability and fertility are negatively coupled within viable systems | N=20, hand-scored, no significance test | Needs larger dataset or reanalysis with explicit statistical testing |
| T2 | Fertile corridor has finite measurable width (0.05–0.10) | N=2-4 fertile per domain, hand-scored | Pattern likely real but precision is spurious |
| T3 | Fertile corridor is NOT a universal attractor | Interpolation model on hand-scored data | Needs actual dynamical perturbation tests, not linear interpolation |
| T4 | Three-zone landscape (collapse → corridor → fortress) | Definitional consequence of scoring criteria | Needs independent evidence that zones are real boundaries, not scoring artifacts |
| T5 | MC3 > MC2 > MC5 > MC4 > MC1 (constraint ranking) | Subjective scoring without blinding | Needs inter-rater reliability or predictive tests |
| T6 | MC2+MC3+MC4 is the minimal constraint set | T081/T082 show generation requires a 4th principle (SP/MC5/MC1) | Claims 10 and 16 are in direct tension with T081/T082 |
| T7 | T078's latent geometry is a cross-domain ensemble property | Equally consistent with "T078 geometry is a hand-scoring artifact" | Needs T084's proposed cross-domain variance test to discriminate |
| T8 | Three-layer architecture (Viability → Mechanisms → Substrate) | Logical organization of findings, not empirically tested | Architectural claim is reasonable but the specific layer content is data-dependent |

### UNJUSTIFIED ASSUMPTIONS (not warranted by evidence presented)

| # | Assumption | Why Unjustified |
|---|------------|-----------------|
| U1 | **"PC1 = Generative Capacity, PC2 = Structural Stability" as discovered universal dimensions** | These are interpretive labels applied to eigenvector loadings from N=30 hand-scored data. No validation that PC1 specifically measures generativity (vs. "overall system richness"). Kaiser=0 suggests no genuine low-D structure. |
| U2 | **"Fertile corridor is a single connected region in latent space"** | 12 points in 3D with spread 0.289 — no null model, no statistical test. Any 12 unimodal points would appear "connected." |
| U3 | **"Maximum fertility at stability 0.72" (precise value)** | One hand-scored hypothetical data point (Super-fertile universe). Precision of 0.72 is unwarranted. |
| U4 | **"NEAR-COMPLETE EMERGENCE — MC2+MC3 generate 8/9 assumptions"** | T081 showed MC2+MC3+MC4 in simulation generates only 2/9 assumptions (22%). The "emergence" claim is a conceptual mapping, not a generative demonstration. |
| U5 | **"MC3 is the deepest layer" (philosophical primacy)** | MC3 scored highest in subjective ranking but T082 shows MC3's role (gating viability) is distinct from assumption generation. Calling it "deepest" is philosophical interpretation, not empirical finding. |
| U6 | **"The book is being treated as a clue" (methodological stance claimed)** | Not auditable — it's a statement of intent, not a result. But worth flagging that this stance was adopted after results were produced, making it post-hoc methodological framing. |
| U7 | **"5/6 failure classes are universal"** | "Universal" from N=4 domains is terminologically overclaimed. "Cross-domain within the tested set" would be accurate. |

---

## Highest-Information Next Experiment

The single experiment that would most reduce uncertainty in the program:

### Test: Blind inter-rater reliability of the T075–T078 domain scoring

**Why:** The entire T075–T078 evidence chain (correlation, geometry, attractors, PCA) depends on the 30 hand-scored configurations. If the scores are reproducible by an independent rater using the same rubrics, the claims gain credibility. If not, the program's quantitative findings rest on a subjective foundation.

**Design:**
1. Give 2–3 independent domain experts (or blinded research assistants) the same scoring rubric used in T073–T078 (definitions of C, P, G, R, S, SR, NP, RC, RD, OE at 0.05–1.00 scale).
2. Have each rater independently score the same 30 system configurations.
3. Measure inter-rater reliability (ICC, Cohen's κ, or correlation) for each axis.
4. Re-run the T075–T078 analyses on the independent ratings.

**Information value:** This test discriminates between:
- **The structure is real** (high inter-rater reliability → the scoring captures genuine properties of the systems)
- **The structure is a scoring artifact** (low inter-rater reliability → the PCA geometry, correlations, and boundaries are properties of one person's judgment, not of the systems)

**Secondary benefit:** Even if reliability is high, the independent scores provide held-out validation for the viability thresholds, fertility signatures, and PCA geometry.

**Alternative (if blind scoring is impractical):**
- Sensitivity analysis: perturb each of the 30×10 = 300 individual scores by ±0.05–0.10 and re-run all analyses. If the PCA geometry, corridor width, and correlations are stable under perturbation, they are robust. If they change meaningfully, they are artifacts of precise score values that may not be meaningful.

---

## Summary

| Category | Count | Key Conclusion |
|----------|-------|----------------|
| Established findings (E1–E8) | 8 | Formal graph results and simulation ablation results survive scrutiny. The strongest evidence is from T056–T069 (dependency graphs) and T082–T083 (generative simulations with ablation). |
| Tentative findings (T1–T8) | 8 | All T075–T078 findings are tentative because they derive from a single hand-scored dataset. The meta-constraint ranking is subjective. The three-layer architecture is a logical organization, not an empirical discovery. |
| Unjustified assumptions (U1–U7) | 7 | The PCA ontology claims, the precise corridor measurements, and the "NEAR-COMPLETE EMERGENCE" verdict are not warranted. T081 experimentally contradicts the emergence claim — the substrate does not emerge from MC2+MC3+MC4 alone when simulated. |

**Net assessment:** The program has genuine formal results (dependency structure, compression, ablation dissociations) wrapped in interpretive claims that go beyond the evidence (PCA ontology, emergence verdict, universal dimensions). The T075–T078 numerical edifice rests on unvalidated hand scoring. The generative simulation program (T081–T083) is methodologically stronger but its results contradict the conceptual conclusions from T079–T080 — a contradiction that has not been resolved.
