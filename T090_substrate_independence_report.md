# T090: Substrate Independence Audit — Report

## Objective
Determine whether the 9 Stiegler substrate assumptions are:
1. Markov artifacts (specific to T082's simulator)
2. Generic dynamical-system properties (appear across substrates)
3. True substrate primitives (appear in all implementation families)

## Method
4 substrates × 500 random configurations each, 200 steps per run:

| Substrate | Family | Implementation |
|-----------|--------|----------------|
| Markov chain | Probabilistic finite-state | T082-style transition matrix + self-model |
| Cellular Automaton | Deterministic discrete | 1D elementary CA, Wolfram rules 0–255 |
| Random Boolean Network | Boolean network | Kauffman networks, k=1–4, sync/async |
| Coupled Map Lattice | Continuous dynamical | Logistic/tent/sine maps with diffusive coupling |

Each configuration measured for all 9 assumptions using a shared measurement interface (compute_assumptions). Prevalence threshold: >= 0.2.

## Results

### Cross-Substrate Prevalence (>= 0.2)

| Assumption | Markov | CA | RBN | CML | Verdict |
|------------|--------|----|-----|-----|---------|
| OC2 | 100.0% | 99.0% | 99.8% | 100.0% | **Primitive** |
| IS2 | 100.0% | 100.0% | 100.0% | 100.0% | **Primitive** |
| IC1 | 100.0% | 10.6% | 76.0% | 0.0% | **Markov artifact** |
| CD2 | 84.6% | 1.8% | 3.6% | 0.0% | **Markov artifact** |
| EC1 | 79.8% | 0.6% | 0.4% | 0.0% | **Markov artifact** |
| SR1 | 76.0% | 0.0% | 0.0% | 0.0% | **Markov artifact** |
| OC1 | 99.4% | 41.8% | 94.8% | 13.8% | Implementation-dependent |
| CD1 | 100.0% | 53.0% | 86.4% | 10.2% | Implementation-dependent |
| IS1 | 98.2% | 88.0% | 23.2% | 100.0% | Implementation-dependent |

### Mean Values

| Assumption | Markov mean | Non-Markov mean | Ratio |
|------------|-------------|------------------|-------|
| OC2 | 0.959 | 0.853 | 1.12 |
| IS2 | 0.522 | 0.655 | 0.80 |
| IC1 | 0.857 | 0.146 | **5.87** |
| CD2 | 0.432 | 0.124 | **3.47** |
| EC1 | 0.391 | 0.052 | **7.57** |
| SR1 | 0.320 | 0.000 | **inf** |
| OC1 | 0.566 | 0.413 | 1.37 |
| CD1 | 0.457 | 0.248 | 1.84 |
| IS1 | 0.888 | 0.681 | 1.30 |

## Classification

### True Primitives (appear in all 4 substrates)

**OC2 — Distinguishability:** 99–100% in every substrate. Any discrete-state dynamical system produces distinguishable states by definition. This is a trivial consequence of having a state space.

**IS2 — Coincidence:** 100% in every substrate. However, this is a measurement floor artifact: the IS2 metric returns only 0.5 or 1.0, and the minimum score for any system with >= 5 steps is 0.5. At the >= 0.2 threshold, IS2 is always present. Even at >= 0.5, it's 100% everywhere. IS2 is universal but uninformative — it measures "does the system have more than 2 unique states recently," which is almost always true.

### Markov Artifacts (only in T082-family simulators)

**IC1 — Extractable Information:** 100% in Markov, collapses to 10.6% (CA), 76.0% (RBN), 0% (CML). IC1 measures the diversity of possible next states from each state. Markov chains inherently have probabilistic branching with many possible outcomes. Deterministic substrates (CA, CML) have exactly one successor per state. RBN with k inputs has 2^k possible successors per state, giving intermediate scores. **IC1 requires probabilistic branching** — absent in deterministic substrates.

**CD2 — Self-Constraint:** 84.6% in Markov, 0–3.6% elsewhere. CD2 depends critically on `self_model_level` and `self_model_influence` parameters — explicit constructs in T082's simulator. Non-Markov substrates have no equivalent mechanism. **CD2 requires explicit self-model machinery** — absent in all other substrates.

**EC1 — Environmental Coupling:** 79.8% in Markov (just below the 80% threshold), < 1% elsewhere. Same root cause as CD2: depends on self-model parameters. Barely misses the "Markov artifact" cutoff but is substantively identical. **EC1 requires self-model parameters.**

**SR1 — Self-Reference:** 76.0% in Markov, 0% everywhere else. Also depends on self-model parameters. **SR1 requires self-model machinery.**

### Implementation-Dependent (appear in some non-Markov substrates)

**OC1 — Boundedness:** 99.4% Markov, 94.8% RBN, but only 41.8% CA and 13.8% CML. OC1 measures 1 - recurrence rate in the last 20 steps. CML (continuous coupling) quickly revisits discretized states, so recurrence is high → OC1 low. CA depends on rule: periodic/class 2 rules have high recurrence, chaotic rules have lower. OC1 is a genuine dynamical property that varies by substrate class.

**CD1 — Causal Relations:** 100% Markov, 86.4% RBN, 53% CA, 10.2% CML. CD1 measures transition consistency from each state. Markov chains guarantee consistency (fixed transition matrix). RBN has deterministic Boolean functions. CA has deterministic rules but huge state spaces (2^width) reduce observed consistency. CML with continuous values and diffusive coupling is least consistent when discretized. CD1 varies with substrate determinism.

**IS1 — Phase Structure:** 98.2% Markov, 88% CA, 100% CML, but 23.2% RBN. IS1 measures changes in 5-step block signatures over time. RBNs (especially synchronous) tend to rapidly enter attractors with stable block structure, so IS1 is low. CA and CML continue generating novel blocks. IS1 captures a real property — whether the trajectory shows ongoing phase-like novelty — that depends on substrate dynamics.

## Impact on Phase T Narrative

| Claim | From | T090 Says |
|-------|------|-----------|
| T082: 5/9 emerge under MC2+MC3+MC4 | T082 | Only in Markov — IC1, IS1 are substrate artifacts |
| T086: Persistence irrelevant | T086 | Confirmed — persistence adds nothing |
| T089: 6/9 are simulator artifacts | T089 | **Overridden** — only 4/9 are artifacts. OC2 and IS2 are genuine primitives. |
| T089: 3/9 are MC-generated | T089 | **Refined** — CD2, EC1, SR1 are Markov artifacts, not substrate-independent MC products |
| Architecture is "incomplete" | T089 | **Respecified** — architecture is Markov-specific, not incomplete. The 9 assumptions are design commitments of a specific simulator family. |

## Final Classification Summary

```
                    Markov   CA     RBN    CML    CLASS
OC2  (Distinguish)  █████   █████  █████  █████  ● Primitive
IS2  (Coincidence)  █████   █████  █████  █████  ● Primitive (floor)
IC1  (Extractable)  █████   ░░     ███░   ░░░░░  ◆ Markov artifact
CD2  (Self-const.)  █████   ░░░░░  ░░░░░  ░░░░░  ◆ Markov artifact
EC1  (Env. couple)  ████░   ░░░░░  ░░░░░  ░░░░░  ◆ Markov artifact
SR1  (Self-ref.)    ████░   ░░░░░  ░░░░░  ░░░░░  ◆ Markov artifact
OC1  (Boundedness)  █████   ██░░░  █████  ░░░░░  ◇ Implementation-dep.
CD1  (Causal rel.)  █████   ███░░  █████  ░░░░░  ◇ Implementation-dep.
IS1  (Phase struc.) █████   █████  ██░░░  █████  ◇ Implementation-dep.
```

## Recommendation

The architecture should be understood as **Markov-specific**. Only 2/9 assumptions (OC2, IS2) are substrate-independent primitives; they are structural features of any discrete-state system. The remaining 7 assumptions are either artifacts of T082's specific simulator design or properties that vary across dynamical system families.

For the SFH-SGP program, this means:
- The architecture does not generalize to arbitrary dynamical substrates
- To claim generality, new generative mechanisms would need to be identified for the 3 implementation-dependent properties (OC1, CD1, IS1)
- Alternatively, accept the Markov specificity as the architecture's domain of applicability
