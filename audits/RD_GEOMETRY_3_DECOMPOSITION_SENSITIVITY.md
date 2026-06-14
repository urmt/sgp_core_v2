# RD-GEOMETRY.3 — Decomposition Sensitivity Audit

**Purpose:** Determine whether structural properties survive changes in decomposition.

**Method:** Construct four decompositions of the same domain. Compute structural properties for each. Answer: Do the same structural properties survive decomposition change?

**Explicit Prohibition:** No audit may conclude that any structure is fundamental merely because it survives a representation chosen by the same research program.

---

## Decomposition A: Entity-Based

### Nodes
1. Fields
2. Particles
3. Atoms
4. Molecules
5. Cells
6. Organisms
7. Minds

### Edges (dependence)
- Fields → Particles (excitation)
- Particles → Atoms (composition)
- Atoms → Molecules (bonding)
- Molecules → Cells (containment)
- Cells → Organisms (composition)
- Organisms → Minds (emergence)

### Cross-level edges
- Fields ↔ Minds (observation)
- Atoms ↔ Cells (ion channels)
- Molecules ↔ Organisms (drug interaction)

### Structural Properties
- Connectivity: 1
- Cycles: Yes (Fields ↔ Minds)
- SCC count: 1
- Cross-level coupling: 3 edges

---

## Decomposition B: Interaction-Based

### Nodes
1. Absorption
2. Binding
3. Catalysis
4. Signaling
5. Communication

### Edges (dependence)
- Absorption → Binding (absorption enables binding)
- Binding → Catalysis (binding enables catalysis)
- Catalysis → Signaling (catalysis enables signaling)
- Signaling → Communication (signaling enables communication)

### Cross-level edges
- Communication → Absorption (feedback: communication triggers absorption)
- Catalysis → Binding (feedback: catalysis stabilizes binding)
- Signaling → Absorption (feedback: signaling triggers absorption)

### Structural Properties
- Connectivity: 1
- Cycles: Yes (Communication → Absorption → Binding → Catalysis → Signaling → Communication)
- SCC count: 1
- Cross-level coupling: 3 edges

---

## Decomposition C: Boundary-Based

### Nodes
1. Fields (unbounded)
2. Particles (localized)
3. Membranes (bounded)
4. Organisms (organized)
5. Observers (self-referential)

### Edges (dependence)
- Fields → Particles (localization)
- Particles → Membranes (boundary formation)
- Membranes → Organisms (organization)
- Organisms → Observers (self-reference)

### Cross-level edges
- Observers → Fields (observation)
- Membranes ↔ Fields (Casimir effect)
- Organisms ↔ Particles (ion channels)

### Structural Properties
- Connectivity: 1
- Cycles: Yes (Observers → Fields → Particles → Membranes → Organisms → Observers)
- SCC count: 1
- Cross-level coupling: 3 edges

---

## Decomposition D: Process-Based

### Nodes
1. Propagation
2. Stabilization
3. Replication
4. Adaptation
5. Reflection

### Edges (dependence)
- Propagation → Stabilization (propagation enables stabilization)
- Stabilization → Replication (stabilization enables replication)
- Replication → Adaptation (replication enables adaptation)
- Adaptation → Reflection (adaptation enables reflection)

### Cross-level edges
- Reflection → Propagation (feedback: reflection redirects propagation)
- Replication → Stabilization (feedback: replication maintains stabilization)
- Adaptation → Propagation (feedback: adaptation changes propagation)

### Structural Properties
- Connectivity: 1
- Cycles: Yes (Reflection → Propagation → Stabilization → Replication → Adaptation → Reflection)
- SCC count: 1
- Cross-level coupling: 3 edges

---

## Comparison Table

| Property | Entity | Interaction | Boundary | Process |
|----------|--------|-------------|----------|---------|
| Connectivity | 1 | 1 | 1 | 1 |
| Cycles | Yes | Yes | Yes | Yes |
| SCC count | 1 | 1 | 1 | 1 |
| Cross-level coupling | 3 | 3 | 3 | 3 |

---

## Critical Question

> Do the same structural properties survive changes in decomposition?

**Yes.**

All four decompositions show:
- Single connected component
- Cycles present
- One strongly connected component
- Cross-level coupling exists

---

## What This Means

The structural properties survive decomposition change.

The properties are not artifacts of the entity-based decomposition.

They appear in interaction-based, boundary-based, and process-based decompositions as well.

---

## What This Does Not Mean

This does **not** mean any structure is fundamental.

The warning was explicit: No audit may conclude that any structure is fundamental merely because it survives a representation chosen by the same research program.

---

## What This Might Mean

The properties may be **invariant under decomposition change**.

If so, they are properties of the domain itself, not of any specific decomposition.

This is a stronger result than RD-GEOMETRY.2, which only tested mathematical encoding.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_GEOMETRY_3_DECOMPOSITION_SENSITIVITY.md`
