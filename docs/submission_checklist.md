# Submission Checklist

## Pre-Submission Verification

### Repository Archive
- [ ] Create GitHub release tagged `PHASE_016_FREEZE`
- [ ] Archive repository as Zenodo DOI
- [ ] Verify DOI resolves to correct commit
- [ ] Add DOI to manuscripts

### Paper 1 — PRE Submission
- [ ] PDF compiles cleanly (5 pages)
- [ ] References resolve (no ? marks)
- [ ] Figures numbered correctly (1-5)
- [ ] Caption text matches figure content
- [ ] No forbidden terminology (grep verified)
- [ ] α = 0.039 ± 0.018 consistent throughout
- [ ] 21 MEC recordings consistent throughout
- [ ] Limitations section includes all 4 items
- [ ] Supplementary materials linked
- [ ] Reproducibility statement included

### Paper 2 — Chaos Submission
- [ ] PDF compiles cleanly (4 pages)
- [ ] References resolve (no ? marks)
- [ ] Figures numbered correctly (1-3)
- [ ] Caption text matches figure content
- [ ] No forbidden terminology (grep verified)
- [ ] α = 0.039 ± 0.018 consistent throughout
- [ ] 21 MEC recordings consistent throughout
- [ ] Limitations section includes all 4 items
- [ ] Methods section complete

### Repository Verification
- [ ] reproduce_figures.py runs from clean install
- [ ] statistical_comparison_demo.py reproduces D_M values
- [ ] phase_015_controls.py --quick loads cached results
- [ ] All 14 submission figures in submission/figures/
- [ ] README.md updated with current values
- [ ] data_manifest.md complete

## arXiv Submission

### Package Contents
- [ ] paper1.pdf
- [ ] paper2.pdf
- [ ] supplementary.tex
- [ ] bibliography.bib
- [ ] reproducibility_statement.md
- [ ] submission/figures/ (14 PDFs)

### Metadata
- [ ] Title: Conservative, empirical
- [ ] Authors: Correct
- [ ] Categories: physics.data-an, q-bio.NC
- [ ] Abstract: No overclaiming
- [ ] Comments: "2 companion papers"

## Journal Submission (PRE)

### Cover Letter
- [ ] Mentions preprocessing-matched controls
- [ ] Mentions covariance-aware statistics
- [ ] Mentions reproducibility repository
- [ ] Conservative language throughout

### Supplementary
- [ ] Repository link included
- [ ] Zenodo DOI included
- [ ] All Phase 015 results documented
