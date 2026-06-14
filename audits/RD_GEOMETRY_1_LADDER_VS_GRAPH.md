# RD-GEOMETRY.1 — Ladder vs Graph Audit

**Question:** Is reality better modeled as a compositional ladder or a persistent interaction graph?

**Method:**
1. Represent each level as a node
2. Add edges for: compositional dependence, energetic dependence, informational dependence, interaction dependence
3. Compute: hierarchy depth, cyclicity, strongly connected components, cross-level edge density

---

## Nodes

1. Fields
2. Particles
3. Atoms
4. Molecules
5. Networks (autocatalytic)
6. Cells
7. Organisms
8. Minds
9. Societies

---

## Edges

### Compositional Dependence (A is made of B)

| From | To | Type |
|------|-----|------|
| Particles | Fields | Particle is excitation of field |
| Atoms | Particles | Atom is nucleus + electrons |
| Molecules | Atoms | Molecule is bonded atoms |
| Networks | Molecules | Network is interacting molecules |
| Cells | Networks | Cell contains autocatalytic networks |
| Organisms | Cells | Organism is composed of cells |
| Minds | Organisms | Mind requires organism |
| Societies | Minds | Society is composed of minds |

### Energetic Dependence (A requires energy from B)

| From | To | Type |
|------|-----|------|
| Particles | Fields | Particle energy from field excitation |
| Atoms | Particles | Atomic energy from electron-nucleus interaction |
| Molecules | Atoms | Molecular energy from chemical bonds |
| Networks | Molecules | Network energy from chemical reactions |
| Cells | Networks | Cellular energy from metabolism |
| Organisms | Cells | Organism energy from cellular metabolism |
| Minds | Organisms | Mind energy from organism metabolism |
| Societies | Minds | Society energy from individual activity |

### Informational Dependence (A contains information from B)

| From | To | Type |
|------|-----|------|
| Atoms | Particles | Atomic structure determined by particle properties |
| Molecules | Atoms | Molecular structure determined by atomic properties |
| Networks | Molecules | Network structure determined by molecular properties |
| Cells | Networks | Genome stores molecular information |
| Organisms | Cells | Body plan stores cellular information |
| Minds | Organisms | Self-model stores organism information |
| Societies | Minds | Culture stores mental information |

### Interaction Dependence (A requires interaction with B)

| From | To | Type |
|------|-----|------|
| Particles | Fields | Particles interact via fields |
| Atoms | Particles | Atoms require electron-nucleus interaction |
| Molecules | Atoms | Molecules require atom-atom interaction |
| Networks | Molecules | Networks require molecule-molecule interaction |
| Cells | Networks | Cells require network-environment interaction |
| Organisms | Cells | Organisms require cell-cell interaction |
| Minds | Organisms | Minds require organism-environment interaction |
| Societies | Minds | Societies require mind-mind interaction |

### Cross-Level Edges (non-adjacent levels)

| From | To | Type |
|------|-----|------|
| Fields | Atoms | Fields interact with atoms (Casimir effect) |
| Particles | Molecules | Particles interact with molecules (scattering) |
| Atoms | Cells | Atoms interact with cells (ion channels) |
| Molecules | Organisms | Molecules interact with organisms (drugs, nutrients) |
| Networks | Minds | Networks interact with minds (neural networks) |
| Cells | Societies | Cells interact with societies (microbiome) |
| Minds | Fields | Minds interact with fields (observation, measurement) |

---

## Graph Properties

### Nodes: 9

### Edges: 43

- Compositional: 8
- Energetic: 8
- Informational: 7
- Interaction: 8
- Cross-level: 7

### Hierarchy Depth

If we consider only compositional edges (A is made of B):
- Fields → Particles → Atoms → Molecules → Networks → Cells → Organisms → Minds → Societies
- Depth: 8

If we include all edges:
- Maximum path length: 8
- But cycles exist (see below)

### Cyclicity

**Cycles exist.**

Example cycle:
- Minds → Organisms → Cells → Networks → Molecules → Atoms → Particles → Fields → Minds (via observation)

This cycle exists because:
- Minds observe fields (measurement)
- Fields compose particles
- Particles compose atoms
- Atoms compose molecules
- Molecules compose networks
- Networks compose cells
- Cells compose organisms
- Organisms compose minds

**The graph is not acyclic.**

### Strongly Connected Components

A strongly connected component is a subset of nodes where every node is reachable from every other node.

**Strongly Connected Component 1:**
- Fields, Particles, Atoms, Molecules, Networks, Cells, Organisms, Minds, Societies

**All nodes are in one strongly connected component.**

This means: From any level, you can reach any other level through a sequence of edges.

### Cross-Level Edge Density

- Total possible edges between non-adjacent levels: 9×8/2 - 8 = 28
- Actual cross-level edges: 7
- Density: 7/28 = 0.25

**25% of possible cross-level edges exist.**

---

## Interpretation

### Ladder Model Assessment

The ladder model assumes:
- Linear composition
- No cycles
- Each level depends only on adjacent lower levels

**Findings:**
- Cycles exist (observation cycle)
- Cross-level edges exist (25% density)
- All levels are in one strongly connected component

**The ladder model is incomplete.**

### Graph Model Assessment

The graph model assumes:
- Non-linear composition
- Possible cycles
- Cross-level dependencies

**Findings:**
- Cycles exist
- Cross-level edges exist
- Strongly connected component includes all levels

**The graph model is more accurate than the ladder model.**

---

## Critical Question

> If many strong cross-level edges exist, the ladder model is incomplete.

**7 cross-level edges exist. 25% density. One strongly connected component.**

**The ladder model is incomplete.**

---

## What This Means

The compositional ladder is a useful approximation but not the correct geometry.

Reality is better modeled as a persistent interaction graph where:
- Cross-level interactions are common
- Cycles exist
- All levels are interconnected

The ladder remains useful for understanding compositional dependence, but it misses:
- Energetic dependence across levels
- Informational dependence across levels
- Interaction dependence across levels
- The observation cycle (minds → fields → particles → ... → minds)

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_GEOMETRY_1_LADDER_VS_GRAPH.md`
