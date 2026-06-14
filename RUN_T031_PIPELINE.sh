#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# T031 NULL GEOMETRY DISENTANGLEMENT — FULL PIPELINE
# ============================================================
# Reproducible execution + validation + artifact checks
# Updated to match ACTUAL T031 outputs and JSON structure
# ============================================================

ROOT="/home/student/sgp_core_v2"
OUT="${ROOT}/sfh_sgp_ood_outputs"
FIG="${ROOT}/figures"
LOG="${ROOT}/logs"

mkdir -p "$LOG"

echo "============================================================"
echo "T031 NULL GEOMETRY DISENTANGLEMENT PIPELINE"
echo "============================================================"

START=$(date +%s)

cd "$ROOT"

# ------------------------------------------------------------
# 1. EXECUTE T031
# ------------------------------------------------------------

echo ""
echo "[1/6] Running T031_NULL_GEOMETRY_DISENTANGLEMENT.py ..."
echo ""

python T031_NULL_GEOMETRY_DISENTANGLEMENT.py \
  2>&1 | tee "${LOG}/t031_pipeline.log"

echo ""
echo "[OK] T031 execution complete."
echo ""

# ------------------------------------------------------------
# 2. VERIFY CORE OUTPUT FILES
# ------------------------------------------------------------

echo "[2/6] Verifying required output artifacts ..."

REQUIRED_FILES=(
  "${OUT}/t031_null_metrics.csv"
  "${OUT}/t031_information_geometry.csv"
  "${OUT}/t031_embedding_stability.csv"
  "${OUT}/t031_geometry_comparison.csv"
  "${OUT}/t031_null_rankings.csv"
  "${OUT}/t031_null_geometry_results.json"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[FAIL] Missing output: $f"
    exit 1
  fi
done

echo "[OK] All required output files found."
echo ""

# ------------------------------------------------------------
# 3. VERIFY FIGURES
# ------------------------------------------------------------

echo "[3/6] Checking generated figures ..."

REQUIRED_FIGS=(
  "${FIG}/fig_t031_null_pr_comparison.png"
  "${FIG}/fig_t031_information_geometry.png"
  "${FIG}/fig_t031_manifold_survival.png"
  "${FIG}/fig_t031_spectral_decay.png"
  "${FIG}/fig_t031_metric_failure_heatmap.png"
)

for f in "${REQUIRED_FIGS[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[FAIL] Missing figure: $f"
    exit 1
  fi
done

echo "[OK] All figures verified."
echo ""

# ------------------------------------------------------------
# 4. EXTRACT FINAL VERDICT
# ------------------------------------------------------------

echo "[4/6] Extracting final decision framework verdict ..."

python - <<'PY'
import json
from pathlib import Path

path = Path("sfh_sgp_ood_outputs/t031_null_geometry_results.json")

with open(path) as f:
    data = json.load(f)

g = data["section_G"]

print("")
print("============================================================")
print("FINAL T031 VERDICT")
print("============================================================")
print(f"Passed Criteria : {g['passed']} / {g['total']}")
print(f"Score            : {g['score']:.3f}")
print(f"Verdict          : {g['verdict']}")
print("")

print("Criteria:")
for item in g["details"]:
    print(" -", item)

print("============================================================")
print("")
PY

# ------------------------------------------------------------
# 5. CONSISTENCY CHECKS
# ------------------------------------------------------------

echo "[5/6] Running consistency checks ..."

python - <<'PY'
import pandas as pd
import numpy as np
from pathlib import Path

out = Path("sfh_sgp_ood_outputs")

metrics = pd.read_csv(out / "t031_null_metrics.csv")
geom = pd.read_csv(out / "t031_geometry_comparison.csv")
embed = pd.read_csv(out / "t031_embedding_stability.csv")

assert len(metrics) >= 7, "Expected >=7 null models"
assert np.isfinite(metrics["pr"]).all(), "Non-finite PR values"
assert np.isfinite(metrics["knn_r"]).all(), "Non-finite kNN scores"

assert len(embed) > 0, "Embedding stability empty"

print("[OK] Metrics finite")
print("[OK] Embedding stability valid")
print("[OK] Geometry comparison table valid")
PY

echo ""
echo "[OK] Consistency checks passed."
echo ""

# ------------------------------------------------------------
# 6. FINAL RUNTIME SUMMARY
# ------------------------------------------------------------

END=$(date +%s)
RUNTIME=$((END - START))

echo "============================================================"
echo "T031 PIPELINE COMPLETED SUCCESSFULLY"
echo "============================================================"
echo "Runtime: ${RUNTIME} seconds"
echo ""
echo "Outputs:"
echo "  - ${OUT}/t031_null_metrics.csv"
echo "  - ${OUT}/t031_information_geometry.csv"
echo "  - ${OUT}/t031_embedding_stability.csv"
echo "  - ${OUT}/t031_geometry_comparison.csv"
echo "  - ${OUT}/t031_null_rankings.csv"
echo "  - ${OUT}/t031_null_geometry_results.json"
echo ""
echo "Figures:"
echo "  - fig_t031_null_pr_comparison.png"
echo "  - fig_t031_information_geometry.png"
echo "  - fig_t031_manifold_survival.png"
echo "  - fig_t031_spectral_decay.png"
echo "  - fig_t031_metric_failure_heatmap.png"
echo ""
echo "Log:"
echo "  - ${LOG}/t031_pipeline.log"
echo "============================================================"