Data Manifest — MEC Recordings
================================

Source
------
Gardner, R. J. et al. (2021). A precise coding of spatial information in the
medial entorhinal cortex. Dryad Digital Repository.
https://doi.org/10.5061/dryad.9s4mw6mh0

Original publication: Gardner, R. J., Hermansen, E., Pachitariu, M., Burak, Y.,
Baas, N. A., Dunn, B. A., Moser, M.-B., & Moser, E. I. (2022). Toroidal
topology of population activity in grid cells. Nature, 602, 123-128.

Contents (14 MEC FRtensor files)
----------------------------------
These are firing-rate tensors from medial entorhinal cortex recordings across
5 laboratories (Goa, Kerala, Mumbai, Hanover, Calais).

| File | N (neurons) | Source lab |
|------|-------------|------------|
| Goa_1207_1_MEC_FRtensor.npy | ~100-200 | Goa |
| Goa_1209_1_MEC_FRtensor.npy | ~100-200 | Goa |
| Goa_1210_1_MEC_FRtensor.npy | ~100-200 | Goa |
| Goa_1211_1_MEC_FRtensor.npy | ~100-200 | Goa |
| Kerala_1207_1_MEC_FRtensor.npy | ~100-200 | Kerala |
| Kerala_1208_1_MEC_FRtensor.npy | ~100-200 | Kerala |
| Kerala_1209_1_MEC_FRtensor.npy | ~100-200 | Kerala |
| Kerala_1210_2_MEC_FRtensor.npy | ~100-200 | Kerala |
| Kerala_1211_1_MEC_FRtensor.npy | ~100-200 | Kerala |
| Kerala_1213_1_MEC_FRtensor.npy | ~100-200 | Kerala |
| Mumbai_1125_1_MEC_FRtensor.npy | ~100-200 | Mumbai |
| Mumbai_1129_1_MEC_FRtensor.npy | ~100-200 | Mumbai |
| Mumbai_1130_1_MEC_FRtensor.npy | ~100-200 | Mumbai |
| Mumbai_1201_1_MEC_FRtensor.npy | ~100-200 | Mumbai |
| Calais_0713_2_MEC_FRtensor.npy | ~50-100 | Calais |
| Hanover_0615_2_MEC_FRtensor.npy | ~50-100 | Hanover |

Tensor shape: (n_timepoints, n_neurons) or (n_trials, n_timepoints, n_neurons).
3D tensors are reshaped to 2D in the analysis pipeline.

Usage
-----
Place files in tier2_data/ and run:
  python reproduce_figures.py

Total size: ~2.1 GB

License
-------
The original data is made available by the authors under the terms of the
Creative Commons CC0 1.0 Universal Public Domain Dedication.
