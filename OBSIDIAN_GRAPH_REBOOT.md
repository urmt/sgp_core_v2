# OBSIDIAN GRAPH REBOOT — SGP-CORE V2

**Date:** 2025-05-13

---

## Purpose

Rebuild knowledge graph in obsidian_graph/ with ONLY empirical V2 content.

No SFH, consciousness, or ontology content.

---

## Graph Structure

```
obsidian_graph/
├── 00_vault_meta/
│   └── VAULT_CONFIG.md
├── 01_concepts/
│   └── (empirical concepts only)
├── 02_methods/
│   └── (pipeline methods)
├── 03_results/
│   └── (findings, not interpretations)
├── 04_systems/
│   └── (domain systems)
├── 05_metrics/
│   └── (quantitative measures)
└── 06_comparisons/
    └── (cross-system analysis)
```

---

## Migration Rules

| Source | Action |
|--------|--------|
| Phase 252-261 (empirical) | KEEP |
| Phase 264 (ontology) | DO NOT MIGRATE |
| SFH manuscripts | DO NOT MIGRATE |
| Visual grounding (empirical) | MIGRATE |
| LaTeX content | MIGRATE |
| Null model specs | MIGRATE |

---

## Vault Configuration

```yaml
# vault settings
graph_metrics: true
backlinks: required
tags: required
metadata: required
```

---

## Content Rules

Allowed content:
- D(k) computation methods
- k0 estimation
- Null model descriptions
- System descriptions (synthetic, physics, neural)
- Metric definitions
- Validation results

Not allowed:
- Consciousness claims
- Sentience references
- "Experience" terminology
- SFH framework
- Philosophical interpretations

---

## Status

**FRAMEWORK DEFINED**  
Next: Content migration from empirical sources