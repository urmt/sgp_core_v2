# RD-METRIC.1: Literature Survey of Existing Scientific Measures Related to Fertility

**Purpose:** Survey existing scientific measures related to complexity, diversity, evolvability, adaptability, open-ended evolution, information generation, and novelty production — to assess which come closest to measuring "fertility" (the capacity of a structure to enable further coherent experience through interaction).

**Date:** 2026-06-14

---

## Table of Contents

1. [Information Theory Measures](#1-information-theory-measures)
2. [Algorithmic & Computational Complexity Measures](#2-algorithmic--computational-complexity-measures)
3. [Statistical Complexity Measures](#3-statistical-complexity-measures)
4. [Ecological Diversity Indices](#4-ecological-diversity-indices)
5. [Evolutionary & Evolvability Measures](#5-evolutionary--evolvability-measures)
6. [Open-Ended Evolution Metrics](#6-open-ended-evolution-metrics)
7. [Novelty Production & Intrinsic Motivation](#7-novelty-production--intrinsic-motivation)
8. [Biological Fitness Measures](#8-biological-fitness-measures)
9. [Summary Table](#9-summary-table)
10. [Relation to Fertility: Evaluation](#10-relation-to-fertility-evaluation)

---

## 1. Information Theory Measures

### 1.1 Shannon Entropy

- **Definition:** A measure of the uncertainty or information content of a random variable. The average amount of surprise produced by a source.
- **Mathematical form:** H(X) = −∑_x p(x) log₂ p(x)
- **Domain:** Information theory, communications, statistical mechanics, ecology
- **Strengths:** Well-founded axiomatically (Khinchin's theorem); widely applicable; additive for independent variables; interpretable in bits
- **Weaknesses:** Only captures first-order statistics (distribution shape); does not capture temporal dynamics, structure, or causation; assumes a fixed alphabet
- **Relation to coherence:** Low — does not measure how parts fit together; measures distributional uncertainty only
- **Relation to fertility:** Partial — high entropy suggests many possible states (potential for novelty), but does not measure whether those states enable *coherent* further states
- **Relation to experience:** Indirect — measures surprise from an observer's perspective, but the observer must be externally defined

### 1.2 Mutual Information

- **Definition:** The amount of information that one random variable contains about another; the reduction in uncertainty about one variable given knowledge of the other.
- **Mathematical form:** I(X;Y) = H(X) − H(X|Y) = ∑_{x,y} p(x,y) log₂ [p(x,y) / (p(x)p(y))]
- **Domain:** Information theory, neuroscience, genetics, machine learning
- **Strengths:** Captures arbitrary (including nonlinear) statistical dependencies; symmetric; zero iff independent
- **Weaknesses:** Symmetric (no directionality); does not capture causal relationships; requires paired observations; can be misleading for high-dimensional distributions
- **Relation to coherence:** Moderate — measures statistical coupling between parts, which is related to coherence but not identical
- **Relation to fertility:** Partial — mutual information between a structure and its environment could indicate how much the structure "knows about" or is coupled to its environment, but does not capture generativity
- **Relation to experience:** Moderate — often used to quantify information available to an observer about a stimulus

### 1.3 Transfer Entropy

- **Definition:** The amount of directed, time-asymmetric information flow from one stochastic process to another; measures how much the past of process X reduces uncertainty about the future of process Y beyond what Y's own past explains.
- **Mathematical form:** TE(X→Y) = H(Y_{t+1}|Y_t) − H(Y_{t+1}|Y_t, X_t)
- **Domain:** Time series analysis, neuroscience, climate science, economics
- **Strengths:** Directional; captures nonlinear causal influence; non-parametric; model-free; reduces to Granger causality for linear processes
- **Weaknesses:** Requires large sample sizes; sensitive to discretization/binning; only captures one-step-ahead prediction; does not distinguish direct from indirect influences without conditioning
- **Relation to coherence:** Moderate — measures directional coupling between parts, which relates to how parts influence each other over time
- **Relation to fertility:** Strong partial match — measures how much one part of a system enables future states of another part; closest to "enabling further experience" in a dynamic sense
- **Relation to experience:** Strong — explicitly about how one process informs/predicts the future of another, which is experience-adjacent

### 1.4 Granger Causality

- **Definition:** A statistical concept of causation: X Granger-causes Y if past values of X contain information about Y that is not contained in past values of Y alone.
- **Mathematical form:** F(Y|X) = log [σ²(Y|Y_past) / σ²(Y|Y_past, X_past)] (for linear VAR models); equivalently expressible via transfer entropy for nonlinear cases
- **Domain:** Economics, neuroscience, time series analysis
- **Strengths:** Well-established statistical framework; computationally tractable; has causal interpretation in linear Gaussian case
- **Weaknesses:** Only linear in standard formulation; requires stationarity assumptions; does not capture true causation (only predictive causation); confounded by latent variables
- **Relation to coherence:** Low — about predictive coupling, not structural fit
- **Relation to fertility:** Moderate — captures the ability of one part to influence future states of another
- **Relation to experience:** Moderate — about prediction and information flow

---

## 2. Algorithmic & Computational Complexity Measures

### 2.1 Kolmogorov Complexity (Algorithmic Information Content)

- **Definition:** The length of the shortest program that produces a given string on a universal Turing machine. A measure of the algorithmic randomness or incompressibility of an individual object.
- **Mathematical form:** K(x) = min{|p| : U(p) = x} (where U is a universal TM)
- **Domain:** Algorithmic information theory, computability theory
- **Strengths:** Foundationally deep; captures all regularities; invariant under renaming; upper-bounds all other computable complexity measures
- **Weaknesses:** Uncomputable; only defined up to an additive constant; not normalized; sensitive to choice of universal machine
- **Relation to coherence:** Low — measures randomness, not structure; random strings are incompressible but incoherent
- **Relation to fertility:** Inverse — high K means the string is random and contains no exploitable regularities for generating new states
- **Relation to experience:** None directly

### 2.2 Logical Depth

- **Definition:** A measure of complexity defined as the computational time required to compute a string from its shortest (or near-shortest) program. Captures the "work" or "depth" embedded in a structure.
- **Mathematical form:** D_s(x) = min{T(p) : |p| − |p*| < s and U(p) = x}, where p* is the shortest program for x and T(p) is computation time
- **Domain:** Computational complexity, physics of computation
- **Strengths:** Captures temporally extended computation (not just description length); vanishes for both random and simple strings; relates to thermodynamic depth; interpretable as "buried evidence of computation"
- **Weaknesses:** Uncomputable in general; requires significance level parameter s; sensitive to universal machine choice; computationally expensive to approximate
- **Relation to coherence:** Moderate — deep structures are those that require coordinated computation, implying structural coherence
- **Relation to fertility:** Moderate — deep structures have "frozen accidents" that could serve as scaffolding for further computation; Bennett argued deep structures are "useful" complexity
- **Relation to experience:** Indirect — Bennett connected depth to physical systems that have undergone many steps of self-organization

### 2.3 Thermodynamic Depth

- **Definition:** A physical analogue of logical depth: the difference between coarse-grained and fine-grained entropy of a macroscopic state, measuring the entropy production (and hence thermodynamic "work") needed to reach that state.
- **Mathematical form:** S_depth = S_coarse − S_fine (entropy production along the process)
- **Domain:** Non-equilibrium thermodynamics, physics of complexity
- **Strengths:** Physically grounded; universal; additive; captures the history of dissipative processes; vanishes for ordered and random states
- **Weaknesses:** Requires knowledge of the process history; difficult to compute for arbitrary systems; physical interpretation limited to thermodynamic systems
- **Relation to coherence:** Moderate — deep states have been shaped by many thermodynamic steps, implying structural organization
- **Relation to fertility:** Moderate — thermodynamically deep states are far from equilibrium and may be more capable of doing work (enabling further changes)
- **Relation to experience:** Indirect — connects to non-equilibrium thermodynamics and the physical substrate of information processing

### 2.4 Effective Complexity

- **Definition:** The information content of the *regularities* of an object, as opposed to its total information content. Defined as the minimal Kolmogorov complexity of a "good theory" (ensemble) that captures the object's structure.
- **Mathematical form:** E(x) = min K(E) such that x is δ-typical for E and Σ(E) ≤ K(x) + Δ (Gell-Mann & Lloyd, 1990; formalized by Ay, Müller, Szkola 2010)
- **Domain:** Algorithmic information theory, philosophy of science
- **Strengths:** Distinguishes structure from randomness; incompressible strings have low effective complexity; captures "meaningful" structure
- **Weaknesses:** Uncomputable; depends on parameters δ, Δ; requires specifying what counts as a "regularity"; no canonical choice of parameters
- **Relation to coherence:** Strong — explicitly measures the regularities (coherent structure) in an object
- **Relation to fertility:** Partial — identifies the structured part of a system that could serve as a basis for further elaboration, but does not directly measure generative capacity
- **Relation to experience:** Indirect — relates to the scientific concept of "explanation" or "theory"

### 2.5 Sophistication (Complexity Theory)

- **Definition:** The complexity of the minimal coarse description that captures the regularities of a string. Defined as the complexity of the minimal sufficient statistic of the string.
- **Mathematical form:** Soph(x) = min{K(M) : M is a minimal sufficient statistic for x} (Koppel & Atlan, 1991; later refined)
- **Domain:** Algorithmic statistics, complexity theory
- **Strengths:** Avoids the problem that Kolmogorov complexity of random strings is maximal; captures "structural" complexity; related to effective complexity
- **Weaknesses:** Uncomputable; sensitive to formalization choices; only defined for individual strings
- **Relation to coherence:** Strong — captures the complexity of the minimal model that explains the structure
- **Relation to fertility:** Partial — a sophisticated structure has enough regularity to be "explained" but not so little that it's trivial
- **Relation to experience:** None directly

---

## 3. Statistical Complexity Measures

### 3.1 LMC Complexity (López-Ruiz, Mancini, Calbet)

- **Definition:** A statistical complexity measure defined as the product of Shannon entropy and disequilibrium (distance from equiprobability). Designed to vanish in both perfectly ordered and perfectly disordered states.
- **Mathematical form:** C_LMC = H · D, where H = Shannon entropy and D = Jensen-Shannon divergence from uniform distribution
- **Domain:** Statistical mechanics, nonlinear dynamics
- **Strengths:** Simple to compute; vanishes at both extremes (order and disorder); captures "intermediate" complexity
- **Weaknesses:** Not extensive (depends nonlinearly on system size); vanishes exponentially in the thermodynamic limit for 1D spin systems; Feldman & Crutchfield showed it is a trivial function of entropy density in extensive modification; unclear what structures it quantifies
- **Relation to coherence:** Partial — captures the balance between order and disorder, but not specific structural coherence
- **Relation to fertility:** Weak — identifies systems at the "edge of chaos" which may be fertile, but does not measure generativity directly
- **Relation to experience:** None directly

### 3.2 Crutchfield's Statistical Complexity (ε-machine complexity)

- **Definition:** The amount of information about the past stored in a process necessary for optimal prediction of its future. Measured as the entropy of the minimal sufficient statistic (causal state) of a stationary stochastic process.
- **Mathematical form:** C_μ = H[μ] where μ is the measure over causal states of the ε-machine
- **Domain:** Computational mechanics, nonlinear dynamics, time series analysis
- **Strengths:** Principled (information-theoretic foundation); captures genuine structural regularity; identifies the causal architecture of a process; well-defined for stationary processes
- **Weaknesses:** Requires knowledge of (or estimation of) the process generating the data; computationally expensive to estimate from finite data; only defined for stationary processes
- **Relation to coherence:** Strong — captures the structural information that enables prediction, which is a form of coherence
- **Relation to fertility:** Strong — a process with high statistical complexity has structure that enables future prediction and generation of structured output
- **Relation to experience:** Strong — the ε-machine is explicitly about the information processing capacity of a process

---

## 4. Ecological Diversity Indices

### 4.1 Shannon Diversity Index (H')

- **Definition:** A measure of species diversity in a community, accounting for both richness (number of species) and evenness (relative abundance).
- **Mathematical form:** H' = −∑_{i=1}^{S} p_i ln(p_i), where S = number of species, p_i = proportion of individuals belonging to species i
- **Domain:** Ecology, biodiversity, microbiome studies
- **Strengths:** Sensitive to rare species; well-understood; widely used; mathematically tractable
- **Weaknesses:** Sensitive to sample size; maximum value depends on S; does not capture species identity or functional diversity; difficult to compare across communities with different S
- **Relation to coherence:** Low — measures diversity of components, not how they fit together
- **Relation to fertility:** Partial — high diversity could mean more potential for novel interactions, but does not measure whether interactions are coherent or productive
- **Relation to experience:** None directly

### 4.2 Simpson's Diversity Index (D)

- **Definition:** The probability that two randomly selected individuals belong to the same species. Inversely related to diversity.
- **Mathematical form:** D = ∑_{i=1}^{S} p_i² (Simpson's concentration); commonly used as 1−D (Gini-Simpson) or 1/D (reciprocal)
- **Domain:** Ecology, biodiversity
- **Strengths:** Less sensitive to sample size than Shannon; intuitive interpretation; emphasizes dominant species
- **Weaknesses:** Does not weight rare species heavily; insensitive to species richness in some formulations; the three forms (D, 1−D, 1/D) are sometimes confused in literature
- **Relation to coherence:** Low — does not measure structural relationships between species
- **Relation to fertility:** Weak — dominance by one species could actually reduce potential for novel interactions
- **Relation to experience:** None directly

### 4.3 Hill Numbers (Effective Number of Species)

- **Definition:** A unified framework that converts diversity indices into "effective numbers of species" (the number of equally-abundant species that would produce the same index value). Parameterized by order q.
- **Mathematical form:** ^qD = (∑_{i=1}^{S} p_i^q)^{1/(1−q)}; for q=0: species richness S; q=1: exponential of Shannon; q=2: reciprocal of Simpson
- **Domain:** Ecology, biodiversity
- **Strengths:** Interpretable as "effective species count"; unifies all diversity indices; mathematically consistent; allows meaningful comparison across communities
- **Weaknesses:** Does not capture functional or phylogenetic diversity; still measures component diversity, not interaction structure; choice of q is subjective
- **Relation to coherence:** Low — effective species count does not capture how species interact
- **Relation to fertility:** Partial — more effective species could mean more potential for novel ecological interactions
- **Relation to experience:** None directly

### 4.4 Chao1 Estimator (Species Richness)

- **Definition:** An estimator of total species richness (including unobserved species) based on the counts of singletons and doubletons in a sample.
- **Mathematical form:** Chao1 = S_obs + f₁²/(2f₂), where f₁ = number of singletons, f₂ = number of doubletons
- **Domain:** Ecology, microbiome studies
- **Strengths:** Accounts for unseen species; non-parametric; widely used in biodiversity assessment
- **Weaknesses:** Only estimates richness, not evenness; assumes a specific sampling model; can be biased with very sparse or very dense samples
- **Relation to coherence:** None — purely about counting types
- **Relation to fertility:** Weak — estimates how many types exist but not whether they interact productively
- **Relation to experience:** None directly

---

## 5. Evolutionary & Evolvability Measures

### 5.1 Mutational Robustness

- **Definition:** The extent to which a phenotype (or fitness) remains constant despite genetic mutations. Measured as the fraction of mutations that are neutral (do not change the phenotype/fitness).
- **Mathematical form:** R = fraction of single-mutation neighbors with same phenotype; or R = 1 − average fitness effect of mutation
- **Domain:** Evolutionary biology, molecular biology, evolutionary computation
- **Strengths:** Empirically measurable; captures system's tolerance to perturbation; relates to neutral network structure; well-studied
- **Weaknesses:** Can be confused with canalization; high robustness may reduce evolvability (tension between robustness and evolvability); context-dependent
- **Relation to coherence:** Strong — robust systems maintain coherent behavior despite perturbation
- **Relation to fertility:** Complex — high robustness preserves existing structure (coherence) but may reduce capacity to generate novelty; low robustness means fragility
- **Relation to experience:** Indirect — robust systems can maintain function across perturbations

### 5.2 Evolvability Index (Protein Structural)

- **Definition:** A measure of a protein's capacity to acquire sequence diversity while maintaining or acquiring new function. In the specific form by Bloom et al., it is the expected change in function per unit of sequence divergence.
- **Mathematical form:** DS = Δ(fitness) / Δ(sequence distance); or more generally, evolvability = E[|Δz|] per unit genotype change (where z is phenotype)
- **Domain:** Molecular evolution, protein evolution, evolutionary computation
- **Strengths:** Quantifies the genotype-phenotype map's openness to novelty; empirically measurable for proteins; captures the "potential" dimension of evolution
- **Weaknesses:** Requires functional assays or fitness landscapes; context-dependent (evolvability depends on the current genotype); difficult to generalize across systems
- **Relation to coherence:** Moderate — a protein that can acquire new function while maintaining structure has a specific kind of coherence
- **Relation to fertility:** Strong — evolvability is precisely the capacity to generate new forms while maintaining function; closest biological analogue to "capacity to enable further coherent experience"
- **Relation to experience:** Indirect — relates to the organism's capacity to generate new phenotypic "experiences" for its environment

### 5.3 Niche Construction Index

- **Definition:** A measure of the degree to which organisms modify their own and each other's niches, thereby altering selection pressures. Can be measured as the rate or magnitude of environmental modification.
- **Mathematical form:** Varies; often qualitative; some quantitative forms: NC_index = Σ (environmental modifications × persistence × fitness effects)
- **Domain:** Evolutionary biology, ecological niche construction theory
- **Strengths:** Captures organism-environment feedback; accounts for extended evolutionary dynamics; recognizes that organisms are not passive recipients of selection
- **Weaknesses:** Difficult to quantify precisely; operationalization varies across studies; theoretical framework still maturing
- **Relation to coherence:** Moderate — niche construction implies organisms are coherent with their environment through mutual modification
- **Relation to fertility:** Strong — niche construction explicitly creates conditions for further evolution; organisms that modify their environment create new possibilities (new niches, new selection pressures)
- **Relation to experience:** Indirect — organisms construct the "experiential" landscape for themselves and other species

---

## 6. Open-Ended Evolution Metrics

### 6.1 MODES Toolbox Metrics

The MODES Toolbox (Dolson et al., 2019) proposes four metrics for open-ended evolution:

#### 6.1.1 Change Potential

- **Definition:** The capacity of a system to undergo structural or behavioral change over time.
- **Mathematical form:** Measured as the rate of change in some system descriptor (e.g., genetic distance, phenotypic change) over time
- **Domain:** Artificial life, evolutionary computation
- **Strengths:** Captures the dynamic nature of evolution; general across systems
- **Weaknesses:** Does not distinguish constructive change from noise; requires choosing a descriptor
- **Relation to coherence:** Low — change can be incoherent
- **Relation to fertility:** Partial — change is necessary but not sufficient for fertility
- **Relation to experience:** Indirect

#### 6.1.2 Novelty Potential

- **Definition:** The capacity of a system to produce novel types (species, behaviors, traits) that were not present before.
- **Mathematical form:** Novelty rate = |{new types at time t}| / Δt; or novelty = 1 − similarity to nearest existing type
- **Domain:** Artificial life, evolutionary computation
- **Strengths:** Directly measures novelty production; related to the concept of "innovation"
- **Weaknesses:** Requires defining what counts as a "type"; does not measure quality or utility of novelty; sensitive to the similarity metric used
- **Relation to coherence:** Low — novelty does not imply coherence
- **Relation to fertility:** Strong — novelty production is a core component of fertility
- **Relation to experience:** Indirect — new types provide new "experiential" possibilities

#### 6.1.3 Complexity Potential

- **Definition:** The capacity of a system to increase in complexity (e.g., genome information content) over time.
- **Mathematical form:** Rate of increase in Kolmogorov complexity, Lempel-Ziv complexity, or similar measure over time
- **Domain:** Artificial life, evolutionary computation
- **Strengths:** Captures the "ratchet" of complexity increase; well-defined using existing complexity measures
- **Weaknesses:** Complexity may increase without enabling new interactions; depends on the chosen complexity measure
- **Relation to coherence:** Moderate — increasing complexity may or may not involve coherent organization
- **Relation to fertility:** Moderate — complexity increase is associated with capacity increase but not identical
- **Relation to experience:** Indirect

#### 6.1.4 Ecological Potential

- **Definition:** The capacity of a system to support ecological interactions (predation, mutualism, competition) among its components.
- **Mathematical form:** Measured as the number or diversity of ecological interaction types observed
- **Domain:** Artificial life, ecology
- **Strengths:** Captures the richness of interactions; relates to the "fertile" interactions between components
- **Weaknesses:** Requires defining interaction types; difficult to generalize across systems
- **Relation to coherence:** Moderate — ecological interactions require coherent relationships between species
- **Relation to fertility:** Strong — ecological interactions are precisely the "further coherent experience" enabled by the system's structure
- **Relation to experience:** Moderate — ecological interactions are a form of "experiential" coupling

### 6.2 Ω Metric (López-Díaz et al., 2025)

- **Definition:** A metric quantifying the sustained production of novel behaviors in dynamic systems by tracking the persistence of different patterns over time.
- **Mathematical form:** Ω = f(persistence of patterns, novelty rate, diversity of sustained patterns) — formal definition involves tracking distinct behavioral types and their lifetimes
- **Domain:** Complex systems, artificial life, random Boolean networks
- **Strengths:** Distinguishes genuine innovation from temporary fluctuations; portable across systems; captures sustainability of novelty
- **Weaknesses:** Relatively new; requires sufficient observation time; sensitive to pattern definition
- **Relation to coherence:** Moderate — persistent novel patterns imply some degree of coherent maintenance
- **Relation to fertility:** Strong — measures sustained novelty production, which is a core aspect of fertility
- **Relation to experience:** Indirect — novel behaviors create new interaction possibilities

### 6.3 Unbounded Evolution (Adams et al., 2017)

- **Definition:** Formal definition: patterns that are non-repeating within the expected Poincaré recurrence time of an isolated system. Innovation: trajectories not observed in isolated systems.
- **Mathematical form:** Unbounded evolution: |T(t)| → ∞ as t → ∞, where T(t) is the set of distinct types at time t; Innovation: trajectories not in the isolated system's trajectory set
- **Domain:** Dynamical systems theory, origin of life research
- **Strengths:** Formally rigorous; generalizes across physical and biological systems; distinguishes true OEE from bounded dynamics
- **Weaknesses:** Requires computing Poincaré recurrence time (impractical for many systems); the distinction between "isolated" and "open" systems requires careful definition
- **Relation to coherence:** Weak — focuses on non-repetition, not structural coherence
- **Relation to fertility:** Strong — unbounded novelty production is the most expansive definition of fertility
- **Relation to experience:** Indirect — non-repeating patterns mean constantly new "experiential" states

---

## 7. Novelty Production & Intrinsic Motivation

### 7.1 Novelty Search (Lehman & Stanley, 2011)

- **Definition:** An evolutionary algorithm that explicitly rewards behavioral novelty rather than task performance. Novelty is measured as the distance to the nearest neighbors in a behavior space.
- **Mathematical form:** Novelty(x) = (1/k) Σ_{i=1}^{k} dist(b(x), b(x_i)), where x_i are the k nearest neighbors in behavior space
- **Domain:** Evolutionary computation, artificial life, reinforcement learning
- **Strengths:** Can outperform objective-based search on deceptive problems; discovers diverse behaviors; useful for exploration; provably explores more of behavior space
- **Weaknesses:** Requires defining behavior characterization; archive management is non-trivial; can produce novelty without utility; sensitive to the distance metric
- **Relation to coherence:** Low — novelty search does not require coherent behaviors
- **Relation to fertility:** Strong — novelty search is designed to maximize the production of new behaviors
- **Relation to experience:** Indirect — new behaviors create new interaction possibilities

### 7.2 Empowerment (Klyubin, Polani, Nehaniv, 2005)

- **Definition:** An information-theoretic measure of an agent's potential to influence its environment. Defined as the channel capacity between actions and future sensor observations.
- **Mathematical form:** E = C(P(S_{t+n} | A_t)) = max_{P(A_t)} I(A_t; S_{t+n}), where C is channel capacity, A_t is action, S_{t+n} is future sensor state
- **Domain:** Artificial intelligence, reinforcement learning, intrinsic motivation
- **Strengths:** Task-independent; agent-centric; does not require external reward; captures "future potential" to influence the world; provably useful for pre-training
- **Weaknesses:** Requires a probabilistic model of the environment; computationally expensive to estimate; only captures the agent's own influence, not the structure of the environment itself; limited to perception-action loops
- **Relation to coherence:** Moderate — empowerment requires a coherent relationship between actions and their effects
- **Relation to fertility:** Strong — empowerment directly measures the capacity of an agent to affect its future states; the closest AI analogue to "capacity to enable further coherent experience"
- **Relation to experience:** Strong — explicitly about the agent's capacity to generate new sensor states through action

### 7.3 Information Gain / Curiosity-Driven Exploration

- **Definition:** The reduction in uncertainty about the environment achieved by taking an action or observing a new state. Related to Bayesian surprise and mutual information.
- **Mathematical form:** IG = H(θ|o) − H(θ|o, s) = I(θ; s | o), where θ is the model parameter, o is observation, s is the new sample
- **Domain:** Reinforcement learning, neuroscience, intrinsic motivation
- **Strengths:** Principled information-theoretic foundation; naturally drives exploration; can be computed incrementally
- **Weaknesses:** Can lead to "noisy TV" problem (seeking randomness); requires a generative model; does not capture coherence of explored states
- **Relation to coherence:** Low — information gain can come from incoherent exploration
- **Relation to fertility:** Moderate — drives the production of new information, but does not require it to be coherent
- **Relation to experience:** Strong — directly about reducing uncertainty through experience

---

## 8. Biological Fitness Measures

### 8.1 Darwinian Fitness

- **Definition:** The expected reproductive success of a genotype or phenotype; the average contribution to the gene pool of the next generation.
- **Mathematical form:** w = number of offspring surviving to reproduce / average number in population (relative fitness); or w = probability of survival × fecundity (absolute fitness)
- **Domain:** Population genetics, evolutionary biology
- **Strengths:** Well-defined; measurable; the fundamental quantity of natural selection; connects genotype to reproductive outcome
- **Weaknesses:** Context-dependent (fitness changes with environment); does not capture the *capacity* for future adaptation; only measures reproductive output, not structural properties; difficult to define for asexual vs. sexual reproduction
- **Relation to coherence:** Low — fitness does not measure how parts fit together
- **Relation to fertility:** Partial — fitness measures reproductive success (a form of "biological fertility"), but does not capture the capacity to enable *further coherent experience* in a structural sense
- **Relation to experience:** Indirect — fitness determines the "experiential" future of the lineage

### 8.2 Inclusive Fitness

- **Definition:** An extension of Darwinian fitness that includes the effects of an individual's actions on the reproductive success of relatives, weighted by genetic relatedness. Hamilton's rule: a trait evolves if −c + Σ_i b_i r_i > 0.
- **Mathematical form:** W_inclusive = W_direct + Σ_i r_i × b_i, where W_direct = personal reproduction, r_i = relatedness to i-th recipient, b_i = effect on i-th recipient's reproduction
- **Domain:** Sociobiology, kin selection theory, evolutionary biology
- **Strengths:** Explains the evolution of altruism; mathematically elegant (Hamilton's rule); empirically testable in some systems; unifies direct and indirect fitness effects
- **Weaknesses:** Controversial (some argue it's not needed when gene-level models suffice); difficult to measure b_i and r_i in natural populations; may not be maximized in all evolutionary scenarios (nonlinear fitness functions)
- **Relation to coherence:** Moderate — inclusive fitness captures the coherence between an individual's genes and those of its social partners
- **Relation to fertility:** Moderate — captures the capacity to propagate genes through both direct reproduction and helping relatives (a form of "enabling further genetic experience")
- **Relation to experience:** Indirect — extends the "experiential" reach of a gene through social interactions

### 8.3 Absolute and Relative Fitness

- **Definition:** Absolute fitness is the ratio of individuals at two time points (survival × reproduction). Relative fitness normalizes by the most fit genotype.
- **Mathematical form:** Absolute: W_abs = N(t+1)/N(t) for a genotype. Relative: w = W_abs(genotype) / W_abs(most fit genotype)
- **Domain:** Population genetics
- **Strengths:** Simple; measurable; foundational for population genetics models
- **Weaknesses:** Context-dependent; does not capture structural properties; only reproductive output
- **Relation to coherence:** None
- **Relation to fertility:** Partial — reproductive success
- **Relation to experience:** None directly

---

## 9. Summary Table

| Metric | Domain | Coherence | Fertility | Experience | Computability |
|--------|--------|-----------|-----------|------------|---------------|
| Shannon Entropy | Information theory | Low | Partial | Indirect | Computable |
| Mutual Information | Information theory | Moderate | Partial | Moderate | Computable |
| Transfer Entropy | Time series / Causality | Moderate | **Strong** | **Strong** | Approximable |
| Granger Causality | Time series / Causality | Low | Moderate | Moderate | Computable |
| Kolmogorov Complexity | Algorithmic IT | Low | Inverse | None | Uncomputable |
| Logical Depth | Computational complexity | Moderate | Moderate | Indirect | Uncomputable |
| Thermodynamic Depth | Non-eq. thermodynamics | Moderate | Moderate | Indirect | Difficult |
| Effective Complexity | Algorithmic IT | **Strong** | Partial | Indirect | Uncomputable |
| Sophistication | Algorithmic IT | **Strong** | Partial | None | Uncomputable |
| LMC Complexity | Statistical mechanics | Partial | Weak | None | Computable |
| Crutchfield's C_μ | Computational mechanics | **Strong** | **Strong** | **Strong** | Approximable |
| Shannon Diversity (H') | Ecology | Low | Partial | None | Computable |
| Simpson's Diversity | Ecology | Low | Weak | None | Computable |
| Hill Numbers | Ecology | Low | Partial | None | Computable |
| Chao1 | Ecology | None | Weak | None | Computable |
| Mutational Robustness | Evolutionary biology | **Strong** | Complex | Indirect | Empirically measurable |
| Evolvability Index | Molecular evolution | Moderate | **Strong** | Indirect | Empirically measurable |
| Niche Construction | Evolutionary biology | Moderate | **Strong** | Indirect | Difficult |
| MODES: Change Potential | Artificial life | Low | Partial | Indirect | Approximable |
| MODES: Novelty Potential | Artificial life | Low | **Strong** | Indirect | Approximable |
| MODES: Complexity Potential | Artificial life | Moderate | Moderate | Indirect | Approximable |
| MODES: Ecological Potential | Artificial life | Moderate | **Strong** | Moderate | Approximable |
| Ω Metric | Complex systems | Moderate | **Strong** | Indirect | Approximable |
| Unbounded Evolution | Dynamical systems | Weak | **Strong** | Indirect | Theoretical |
| Novelty Search | Evolutionary computation | Low | **Strong** | Indirect | Computable |
| Empowerment | AI / Intrinsic motivation | Moderate | **Strong** | **Strong** | Approximable |
| Information Gain | RL / Neuroscience | Low | Moderate | **Strong** | Approximable |
| Darwinian Fitness | Population genetics | Low | Partial | Indirect | Measurable |
| Inclusive Fitness | Sociobiology | Moderate | Moderate | Indirect | Difficult |

---

## 10. Relation to Fertility: Evaluation

### Working Definition of Fertility

> **Fertility:** The capacity of a structure to enable further coherent experience through interaction.

This definition has three key components:
1. **Capacity** — the structure must be *able* to do something, not just be in a certain state
2. **Enable further** — the structure must be *generative*, not merely descriptive
3. **Coherent experience** — what it enables must be structured, not random; the "experience" must have internal consistency

### Closest Existing Metrics

**Tier 1: Strongest partial matches**

1. **Empowerment** — Most directly captures "capacity to enable further experience." It measures the channel capacity between an agent's actions and future sensor states, which is precisely the capacity to generate diverse future experiences through interaction. However, it is agent-centric and does not measure the *structure's* intrinsic fertility independent of an agent.

2. **Transfer Entropy** — Captures directed information flow between processes, measuring how much one process enables future states of another. This is structurally similar to "enabling further coherent experience." However, it measures a specific pairwise relationship, not the fertility of a structure as a whole.

3. **Crutchfield's Statistical Complexity (C_μ)** — Measures the information processing capacity of a process (how much past information is needed to predict its future). A process with high C_μ has rich internal structure that generates structured future states. This captures both coherence and generativity.

4. **Evolvability Index** — In biology, evolvability is precisely the capacity to generate heritable phenotypic variation that can fuel adaptation. This is the biological analogue of "capacity to enable further coherent experience." However, it is defined relative to fitness landscapes.

**Tier 2: Strong partial matches**

5. **Ecological Potential (MODES)** — Measures the capacity of a system to support ecological interactions. These interactions are "further coherent experience" enabled by the system's structure. However, it only measures one aspect of fertility.

6. **Niche Construction** — Organisms that construct niches create conditions for further evolution. This is a structural capacity to enable further coherent experience. However, it is measured as a rate or magnitude, not as an intrinsic capacity.

7. **Effective Complexity / Sophistication** — Measures the complexity of the *regularities* in a structure. A structure with high effective complexity has coherent internal structure that could serve as a basis for further elaboration. However, these measures do not directly capture generativity.

8. **Logical Depth** — Deep structures are those that require significant computation to produce, implying they contain "buried" structure that could be "unpacked" through further computation. Bennett argued deep structures are "useful" complexity. However, depth measures the process that *produced* the structure, not its capacity to *produce further* experience.

**Tier 3: Partial matches**

9. **Mutational Robustness** — Robust structures maintain coherent behavior, which is necessary for fertility but not sufficient. A robust system can sustain its structure for future interaction but may not generate new interactions.

10. **Novelty Search / Novelty Potential** — Directly measures novelty production, but does not require coherence of what is produced.

11. **Shannon Diversity / Hill Numbers** — Measure the diversity of components, which is related to potential for novel interactions, but do not measure whether interactions are coherent or productive.

**Key Gap Identified**

No existing metric simultaneously captures all three components of fertility:
- **Capacity** (empowerment does this best)
- **Generativity** (novelty search / OEE metrics do this best)
- **Coherence** (effective complexity / statistical complexity do this best)

The closest single metric is **Crutchfield's Statistical Complexity (C_μ)**, which captures both the structural information (coherence) and the predictive/generative capacity of a process. However, it does not explicitly measure the *capacity to enable interaction with an external observer or environment*.

**Empowerment** is the closest in spirit to the project's definition, but it is defined relative to an agent, not as an intrinsic property of a structure. A metric of *structural empowerment* — the channel capacity between a structure's internal states and its observable effects on an environment — would be a natural synthesis.

### Recommendation

No existing metric surveyed appears to fully capture the project's current working notion of fertility. The closest candidates are:
- **Transfer Entropy** (for pairwise enabling)
- **Crutchfield's C_μ** (for structural generative capacity)
- **Empowerment** (for capacity to affect future states)
- **Evolvability** (for biological generativity)

None of these captures the full definition, particularly the requirement that the enabled experience be *coherent* (structured, not random) and that the capacity be *intrinsic to the structure* (not relative to an external agent).

---

*End of survey.*
