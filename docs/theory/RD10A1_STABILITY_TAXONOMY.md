# RD-10A.1: Stability Taxonomy

**Status**: COMPLETE  
**Date**: 2026-06-10  
**Purpose**: Collect stable entities across domains. Classify why stable, what protects, what it enables.

---

## Method

For each stable entity:
1. What is it?
2. Why is it stable? (mechanism)
3. What protects it? (symmetry, conservation, topology, energy)
4. Can it combine with other stable entities?
5. What new class does the combination enable?

---

## Domain 1: Physics

### Electron
- **What**: Elementary particle, lepton, charge -1
- **Why stable**: Conservation of electric charge, conservation of lepton number, no lighter charged lepton exists to decay into
- **What protects it**: Symmetry (gauge symmetry of QED), conservation laws (Noether), Pauli exclusion (degeneracy pressure)
- **Combinability**: Yes — binds to protons via electromagnetic force
- **What it enables**: Atoms. The electron is the first step in the compositional ladder from particle to chemistry.

### Proton
- **What**: Bound state of 3 quarks (uud), baryon number +1
- **Why stable**: Conservation of baryon number, color confinement, mass gap (lightest baryon)
- **What protects it**: Strong force symmetry (QCD gauge symmetry), confinement (no free quarks), baryon number conservation
- **Combinability**: Yes — binds to electrons (atoms), to neutrons (nuclei)
- **What it enables**: Nuclei, atoms, the entire periodic table

### Photon
- **What**: Gauge boson of electromagnetic force, massless
- **Why stable**: Cannot decay (nothing lighter to decay into), gauge symmetry of QED
- **What protects it**: Gauge invariance, masslessness
- **Combinability**: Yes — mediates interactions, can be absorbed/emitted
- **What it enables**: Electromagnetic interaction itself. The photon is not a "part" in the compositional ladder — it is the glue that makes composition possible.

### Atomic Nucleus
- **What**: Bound state of protons and neutrons
- **Why stable**: Strong nuclear force (short-range attraction), binding energy > 0
- **What protects it**: Strong force, nuclear magic numbers (shell structure), energy minimum
- **Combinability**: Yes — electrons orbit nuclei → atoms
- **What it enables**: The periodic table. Chemical diversity.

### Atom
- **What**: Nucleus + electrons in electromagnetic bound state
- **Why stable**: Coulomb attraction, quantum mechanical stability (ground state energy minimum), Pauli exclusion
- **What protects it**: Electromagnetic symmetry, quantum mechanics, energy minimization
- **Combinability**: Yes — chemical bonds → molecules
- **What it enables**: Chemistry. The entire molecular world.

---

## Domain 2: Chemistry

### Molecule
- **What**: Two or more atoms bound by chemical bonds
- **Why stable**: Covalent/ionic bonds lower energy, molecular orbital stability
- **What protects it**: Bond energy, molecular symmetry, Pauli exclusion between electrons
- **Combinability**: Yes — reactions produce new molecules
- **What it enables**: Chemical diversity, functional groups, polymers

### Autocatalytic Set
- **What**: Collection of molecules where each molecule's production is catalyzed by another molecule in the set
- **Why stable**: Self-reinforcing reaction network, closure under catalysis
- **What protects it**: Catalytic closure (no external catalyst needed), self-maintenance
- **Combinability**: Partially — sets can merge or compete
- **What it enables**: Self-maintaining chemistry. Proto-metabolism.

### Crystal
- **What**: Periodic arrangement of atoms/molecules
- **Why stable**: Energy minimum (lattice energy), translational symmetry
- **What protects it**: Symmetry (space group), energy minimization, rigidity
- **Combinability**: Limited — crystals can be composed into larger structures
- **What it enables**: Structural materials, but limited compositional depth

---

## Domain 3: Biology

### Cell
- **What**: Self-maintaining, self-reproducing chemical system enclosed by a membrane
- **Why stable**: Metabolic network maintains components, membrane maintains boundary, DNA maintains information
- **What protects it**: Homeostasis (feedback), membrane (boundary), genetic code (information preservation)
- **Combinability**: Yes — cells form tissues, colonies, biofilms
- **What it enables**: Multicellular life, differentiation, specialization

### Organism
- **What**: Coordinated multicellular system with division of labor
- **Why stable**: Homeostasis at organism level, immune system, developmental program
- **What protects it**: Redundancy (multiple cells), modularity (organs), feedback (hormonal, neural)
- **Combinability**: Yes — mating, symbiosis, social groups
- **What it enables**: Populations, ecosystems, evolution

### Species / Ecosystem
- **What**: Interconnected population of organisms with shared gene pool
- **Why stable**: Natural selection maintains适应性, niche construction, co-evolution
- **What protects it**: Genetic diversity, ecological niches, trophic structure
- **Combinability**: Yes — ecosystems compose into biospheres
- **What it enables**: Macroevolution, adaptive radiation

---

## Domain 4: Information

### Error-Correcting Code
- **What**: Encoding that detects/corrects errors in transmission
- **Why stable**: Redundancy (extra bits), algebraic structure (codes form vector spaces)
- **What protects it**: Distance property (minimum Hamming distance), algebraic structure
- **Combinability**: Yes — codes can be concatenated, nested
- **What it enables**: Reliable communication, reliable computation

### Attractor (Dynamical Systems)
- **What**: Set of states toward which a system evolves
- **Why stable**: Basin of attraction (nearby states converge), Lyapunov stability
- **What protects it**: Dissipation, contracting dynamics
- **Combinability**: Limited — attractors can coexist in state space
- **What it enables**: Robust behavior, memory, oscillation

### Self-Replicator
- **What**: System that produces copies of itself
- **Why stable**: Replication maintains population despite decay of individuals
- **What protects it**: Replication rate > decay rate, error correction (proofreading)
- **Combinability**: Yes — replicators compete, cooperate, form hypercycles
- **What it enables**: Evolution, open-ended adaptation

### Turing Machine / Universal Computer
- **What**: System capable of simulating any computable process
- **Why stable**: Discrete states, deterministic transitions, error correction possible
- **What protects it**: Logical structure, discreteness
- **Combinability**: Yes — computers compose, network, form distributed systems
- **What it enables**: Computation, simulation, science, technology

---

## Cross-Domain Pattern

| Entity | Stability Mechanism | Protection | Composes Into |
|--------|-------------------|------------|---------------|
| Electron | Conservation laws | Symmetry | Atoms |
| Proton | Confinement, conservation | Strong force | Nuclei |
| Atom | Energy minimum | QM, EM | Molecules |
| Molecule | Bond energy | Orbital structure | Chemistry |
| Autocatalytic set | Catalytic closure | Self-maintenance | Proto-metabolism |
| Cell | Homeostasis | Membrane, feedback | Tissues |
| Organism | Redundancy, modularity | Immune system | Populations |
| Error-correcting code | Redundancy | Algebraic structure | Reliable computation |
| Self-replicator | Replication > decay | Proofreading | Evolution |

---

## Observation

Every entity in this table is stable.

But only some are **fertile** — they combine to create new classes of entities.

The electron is fertile (enables atoms → chemistry → biology).  
The crystal is less fertile (limited compositional depth).  
The dead rock is stable but not fertile at all.

**Stability is necessary but not sufficient for fertility.**

The question is: what distinguishes fertile stability from inert stability?
