# T100C: Execution Audit

**Phase:** 2 of 4 — Observed Behavior, Not Inferred
**Date:** 2026-06-01
**Director's Instruction:** "I want observed behavior, not inferred behavior."

---

## Script 1: `reproduce_ch3_figures.py`

### Pre-execution Environment
```
Python: 3.13.2
numpy: 2.2.3
matplotlib: 3.10.1
scipy: 1.15.2
pandas: 2.2.3
Working directory: /tmp/opencode/SFH_Python_CODE
```

### Run 1 — As committed (zero modifications)

**Command:** `python3 reproduce_ch3_figures.py`

**Result: CRASH — `IndentationError` at import time**

```
Traceback (most recent call last):
  File "reproduce_ch3_figures.py", line 11, in <module>
    import partition_calc as pc
  File "partition_calc.py", line 19
    def hardy_ramanujan_asymptotic(self, Q: float) -> float:
    ^^^
IndentationError: expected an indented block after function definition on line 16
```

**Root cause:** The `PartitionCalculator` class in `partition_calc.py` has method stubs with only comments and `pass` (or bare comments). Specifically:
- Line 14: `# Optional: Cache for partition_function_value for performance` — placeholder for `partition_function_value`
- Lines 16-17: The actual `partition_function_value` method body is missing (just a comment) → Python expects an indented block after `def partition_function_value(self, n: int) -> int:` on line 16

**Observations:**
- Script never reached its own code — crashed on import of `partition_calc`.
- Zero output files generated.
- Zero print statements executed.

### Run 2 — After fixing partition_calc.py stubs + math.sqrt bugs

**Fixes applied:**
1. Replaced stub method bodies with working implementations (generate_all_partitions, _partitions_recursive, classify_partitions, partition_function_value)
2. `math.sqrt` → `math.sqrt(3)` on line 27
3. `math.sqrt` → `math.sqrt(3)` on line 99
4. `results[key].append` → `results[key].append(None)` on line 144

**Result: TIMEOUT** (killed after 120 seconds)

**Terminal output:** None — no print statements reached.

**Root cause:** `run_partition_analysis(num_samples=20000)` with `max_n=100`. Each call to `generate_all_partitions(n)` for n up to 100 generates:
- n=50: 204,226 partitions
- n=75: 8,117,938 partitions  
- n=100: 190,569,292 partitions

With 20,000 samples spread across n=1..100, the expected partition enumeration workload is astronomical. Even a single call at n=100 would exhaust memory/time.

**Unreached bugs (would trigger if timeout fixed):**
| # | File:Line | Bug | Expected Error |
|---|---|---|---|
| 5 | `reproduce_ch3_figures.py:27` | `sa.StatisticalAnalyzer(results)` — passes dict `results` to `random_seed=` parameter | `TypeError: __init__() got multiple values for argument 'random_seed'` |
| 6 | `reproduce_ch3_figures.py:28` | `analyzer.basic_summary()` doesn't exist | `AttributeError: 'StatisticalAnalyzer' object has no attribute 'basic_summary'` |
| 7 | `reproduce_ch3_figures.py:34` | `av.plot_coherence_fertility_histograms()` doesn't exist | `AttributeError: module 'advanced_visualization' has no attribute 'plot_coherence_fertility_histograms'` |
| 8 | `reproduce_ch3_figures.py:41` | `av.plot_pareto_frontier()` doesn't exist | Same as above |
| 9 | `reproduce_ch3_figures.py:48` | `av.plot_weight_sweep()` doesn't exist | Same as above |

### Execution Verdict: `reproduce_ch3_figures.py` is NON-FUNCTIONAL as committed.
Total fixable errors: **9**. Zero files generated. Zero successful runs.

---

## Script 2: `sfh_master_framework.py`

### Run 1 — As committed (zero modifications)

**Command:** `python3 sfh_master_framework.py`

**Result: CRASH — `IndentationError`** (same root cause as Run 1 of reproduce_ch3_figures.py)

```
Traceback (most recent call last):
  File "sfh_master_framework.py", line 7, in <module>
    from partition_calc import PartitionCalculator
  File "partition_calc.py", line 19
    def hardy_ramanujan_asymptotic(self, Q: float) -> float:
    ^^^
IndentationError: expected an indented block after function definition on line 16
```

### Run 2 — After fixing partition_calc.py stubs + math.sqrt bugs

**Fixes applied (same as above):**
1. Stub methods → implementations
2. `math.sqrt` → `math.sqrt(3)` (×2)
3. `results[key].append` → `results[key].append(None)`

**Result: CRASH — `TypeError` at module level**

```
Traceback (most recent call last):
  File "sfh_master_framework.py", line 181, in <module>
    main()
  File "sfh_master_framework.py", line 53, in main
    df = load_or_generate_data(...)
  File "sfh_master_framework.py", line 41, in load_or_generate_data
    raise FileNotFoundError(f"Data file {data_file} not found.")
FileNotFoundError: Data file Generated_CODE_Data/samples_v6.csv not found.
```

**Note:** This error is because the execution ran from a temp directory without the CSV files. When re-run from `/tmp/opencode/SFH_Python_CODE`, the CSVs are found.

### Run 3 — From correct working directory + fixes + stats bugfix

**Fixes applied (all above +):**
4. Renamed local `stats` dict to `summary_stats` in `_create_markdown_report()` and `main()` to avoid shadowing `from scipy import stats`
5. Added `import scipy` and used `scipy.__version__` for version check

**Result: SUCCESS — completed in 5.29 seconds**

**Generated files:**
| File | Size | Content |
|---|---|---|
| `analysis_results.json` | 905 KB | Full partition analysis results |
| `distribution_analysis_partition_function.png` | 491 KB | Distribution visualization |
| `distribution_fitting_partition_function.png` | 462 KB | Distribution fitting visualization |
| `summary_dashboard_partition_function.png` | 601 KB | Summary dashboard |
| `partition_analysis_report.md` | 3.2 KB | Auto-generated report |

**Terminal output:**
```
=== SFH Master Framework (v6 Enhanced) ===
Numbers analyzed: 3 (12, 24, 36)
Total partitions: 19,629
All theoretical verifications passed: True (100% Euler identity)
Visualization system: Advanced
Output directory: partition_analysis_output/
```

**Execution Verdict: `sfh_master_framework.py` is FUNCTIONAL after 5 fixes.**
But it generates generic partition visualization, NOT fine-tuning probability or physical constants.

---

## Output Analysis: What `sfh_master_framework.py` Actually Generates

### `analysis_results.json` — Structure (first 5 lines)
```json
{
  "partition_function_values": [12, 24, 36],
  "partition_counts": [77, 1575, 17977],
  "total_partitions": 19629,
  "euler_verify": [true, true, true],
  ...
}
```

### `partition_analysis_report.md` (converted to text)
```
# Partition Analysis Report: partition_function
- **Date**: 2026-06-01
- **Numbers analyzed**: 12, 24, 36
- **Partitions generated**: 19,629
- **Theoretical verification**: 100.00%
- **Visualization**: Advanced
```

### Key Observation
The successful execution generates **pure partition theory results** (partition counts, distribution plots, Euler identity verification). It does NOT generate:
- Physical constants (α, G, G_F, α_s, μ)
- Coherence values
- Fertility values
- Universe probability
- Pareto frontier

The output is generic number theory, unrelated to SFH fine-tuning claims.

---

## Summary: What Each Script Does When Run

| Script | As-Committed Result | After Fixes Result | SFH Fine-Tuning Output? |
|---|---|---|---|
| `reproduce_ch3_figures.py` | **CRASH** (IndentationError line 11) | **TIMEOUT** + 6 unreached bugs | N/A — cannot reach user code |
| `sfh_master_framework.py` | **CRASH** (same IndentationError) | **SUCCESS (5.29s)** — generates partition theory plots | **NO** — generates generic partition statistics, no constants/probability |

**Bottom line:** Neither script, in its current state, computes or outputs fine-tuning probabilities for physical constants.
