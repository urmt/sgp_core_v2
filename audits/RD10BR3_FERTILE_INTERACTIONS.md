# RD-10B.R3: Fertile Interaction Audit — Report

## Status: COMPLETE

---

## Question

What configuration of interaction produces fertility?

Not: "Is interaction fundamental?"
But: "What configuration of interaction produces persistent novelty?"

---

## The Actual Claim

> Persistent novelty emerges when coherent structures can interact without collapsing each other.

This requires four components:
1. **Interaction** — structures are in contact
2. **Persistence** — the interaction doesn't destroy the structures
3. **Novelty** — something new emerges from the interaction
4. **Coherence** — the structures are internally consistent

---

## Results

### Configuration Counts

| Configuration | Audits | Gain | Rate |
|--------------|--------|------|------|
| I+C (falsifications) | 6 | 6 | 100% |
| I+N+C | 2 | 2 | 100% |
| I+P+N | 2 | 2 | 100% |
| I+P+N+C (successes) | 14 | 14 | 100% |
| I+P+N+C (abandoned) | 1 | 0 | 0% |

### Key Finding

I+C has 100% gain rate. I+P+N+C has 100% gain rate (excluding abandoned).

P+N does NOT add predictive power for gain.

But the theory is not about gain. It is about **persistent novelty**.

---

## Two Types of Gain

### 1. Falsification Gain (I+C)

- RD-019: density does not explain C
- RD-020: structural importance does not explain C
- RD-021: velocity field does not explain C
- RD-9E: SP is binary artifact
- RD-10B.3: detectors measure time-series
- RD-10B.M1: migration is methodological

These produce gain by **destroying old structure**.
They do not need persistence or novelty.
They just need interaction + coherence.

### 2. Persistent Novelty Gain (I+P+N+C)

- RD-5: C is projection of MSE
- RD-10A.8-12: constraint framework
- RD-10B.0-0F: representation and identity
- RD-10B.J2-J8: independence testing
- RD-10B.M6b: viewpoint vs claim

These produce gain by **creating new structure**.
They need all four components.

---

## The Abandoned Experiment

`interaction_first` had I+P+N+C but no gain.

Why?

Because the experiments were never completed.
The code was written. The results don't exist.

This is the crucial counterexample:

> I+P+N+C (possible) ≠ I+P+N+C (actual)

Possible interaction is not enough.
Actual interaction is required.

---

## The Refined Theory

### Original Claim

> Persistent novelty emerges when coherent structures can interact without collapsing each other.

### Refined Claim

> Persistent novelty emerges when coherent structures **actually** interact without collapsing each other.

The word "actually" is doing all the work.

---

## Implications

### For the Program

The theory is not about interaction in general.
It is about **actual interaction** between **coherent structures** that **persist** through the interaction.

### For Future Audits

When testing the theory, we must distinguish:
- Possible interaction (code exists, not run)
- Actual interaction (experiments completed, results obtained)

### For Standing Rules

**SR-24**: Distinguish possible interaction from actual interaction. Possible interaction is not enough. Actual interaction is required for persistent novelty.

---

## Files

- `audits/rd10br3_fertile_interactions.py` — R3 experiment
- `audits/rd10br3b_component_analysis.py` — R3b re-examination
- `audits/RD10BR3_FERTILE_INTERACTIONS.md` — this report
