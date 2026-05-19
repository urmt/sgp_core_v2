# CROSS-DOMAIN ROADMAP — SGP-CORE V2

**Date:** 2025-05-13

---

## Domain Integration Strategy

### Phase 1: Synthetic Validation (Priority: HIGH)

**Goal:** Validate infrastructure on controlled systems before adding real domains

Systems to test:
1. Random clouds (null baseline)
2. Hierarchical clusters (known structure)
3. Sparse graphs (network topology)
4. Dynamical attractors (time evolution)
5. Transformer embeddings (artificial system)

**Status:** EMPIRICAL_CORE_SPEC defines this

---

### Phase 2: Physics Systems (Priority: MEDIUM)

Systems to add:
- Turbulent flows (fluid dynamics)
- Quantum systems (many-body)
- Lattice systems (statistical mechanics)
- Spin models (Ising, XY)

**Requirement:** Pass Phase 1 first

---

### Phase 3: Neuroscience (Priority: MEDIUM)

Systems to add:
- Neural activity data (e.g., Allen Institute)
- Connectome data (whole brain)
- Spike train data
- LFP/EEG recordings

**Requirement:** Pass Phase 1 first

---

### Phase 4: Ecology (Priority: LOW)

Systems to add:
- Ecosystem dynamics
- Food webs
- Population models
- Species interaction networks

**Requirement:** Pass Phases 1-3 first

---

## Domain-Specific Considerations

| Domain | Expected k0 | Expected D(k) Shape | Special Notes |
|--------|-------------|---------------------|---------------|
| Random | Undefined | Flat | Null baseline |
| Hierarchical | Multiple | Multi-regime | Scale-specific |
| Networks | Connectivity-dependent | Topology-based | Graph metrics |
| Dynamical | Attractor-based | Temporal variation | Time-evolving |
| Transformer | Layer-dependent | Architecture-specific | Reproduce prior |
| Physics | System-dependent | Scale-invariant | Physics-constrained |
| Neuroscience | Function-dependent | Multi-scale | Brain-architecture |
| Ecology | Interaction-dependent | Diversity-structured | Ecosystem invariants |

---

## Integration Tests

Each domain must pass:
1. Synthetic validation (Phase 1 pass)
2. Null model comparison
3. Reproducibility check
4. Cross-domain comparison

---

## Status

**Phase 1: IN PROGRESS** (building synthetic validation)  
**Phases 2-4: PENDING** (must pass Phase 1 first)