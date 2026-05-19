# GITHUB CLEANROOM SETUP REPORT

**Date:** 2025-05-13  
**Status:** COMPLETE

---

## Created Files

| File | Purpose |
|------|---------|
| `.gitignore` | Enforce cleanroom rules |
| `README.md` | Project documentation |

---

## .gitignore Rules

### Exclude (DO NOT PUSH)
- Raw data: `*.npy`, `*.npz`, `*.pkl`, `*.h5`, `outputs/raw/*`
- Publication: `*.tex`, `*.pdf`, `*.bib`
- Temporary: `temp/`, `cache/`, `__pycache__/`
- Notebooks: `*.ipynb`, `.ipynb_checkpoints/`

### Include (PUSH)
- `.py` scripts
- `.md` documentation
- `.json` metadata
- `.csv` tables
- Generated figures
- Logs and reproducibility docs

---

## README Contents

- Project purpose (empirical infrastructure)
- Reproducibility instructions
- Quick start commands
- Directory structure
- Known limitations reference

---

## Status

**COMPLETE**  
Repository lightweight, reproducible, publication-clean ready.