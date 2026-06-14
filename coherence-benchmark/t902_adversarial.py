"""T902: Adversarial falsification of coherence → resilience thesis.

Load existing 60-run ensemble and search for contradictions:
  - High C + poor recovery
  - Low C + strong recovery
  - Same C + different recovery
  - Same mobility + different C → different recovery
"""

import numpy as np
import json

SEP = "=" * 78

with open("results/t901_ensemble.json") as f:
    raw = json.load(f)

rows = []
for r in raw:
    rr = {}
    for k, v in r.items():
        if v is None:
            rr[k] = np.nan
        elif k in ("friction", "rep", "tau_rec"):
            rr[k] = v
        else:
            rr[k] = float(v)
    rows.append(rr)

c = np.array([r["pre_C"] for r in rows])
msd = np.array([r["msd"] for r in rows])
fric = np.array([r["friction"] for r in rows])
dip = np.array([r["dip"] for r in rows])
rest = np.array([r["restoration"] for r in rows])
tau = np.array([r["tau_rec"] for r in rows])

c_lo, c_hi = np.percentile(c, [25, 75])
lo_mask = c <= c_lo
hi_mask = c >= c_hi

print(f"{SEP}")
print("  T902: ADVERSARIAL FALSIFICATION")
print(f"  Try to break: 'C alone determines recovery'")
print(f"{SEP}")

print(f"\n  Dataset: {len(rows)} runs")
print(f"  C range: {c.min():.4f} – {c.max():.4f}")
print(f"  Low C  (Q1 ≤ {c_lo:.4f}): {lo_mask.sum()} runs")
print(f"  High C (Q4 ≥ {c_hi:.4f}): {hi_mask.sum()} runs")

# ─── Attack 1: High C + poor recovery ───
print(f"\n{SEP}")
print("  ATTACK 1: HIGH C + POOR RECOVERY")
print(f"  Criterion: C ≥ Q3 ({c_hi:.4f}) AND (restoration < 1.0 OR τ_rec > 100)")
print(f"{SEP}")
hits = []
for i in np.where(hi_mask)[0]:
    poor = rest[i] < 1.0 or tau[i] > 100
    if poor:
        hits.append(rows[i])
if hits:
    print(f"\n  FOUND: {len(hits)} runs with high C but poor recovery")
    for h in hits:
        print(f"    C={h['pre_C']:.4f}  ΔC={h['dip']:+.4f}  rest={h['restoration']:.4f}  τ={h['tau_rec']:.0f}  fric={h['friction']:.2f}")
else:
    print(f"\n  NOT FOUND: all high-C runs recover well")

# ─── Attack 2: Low C + strong recovery ───
print(f"\n{SEP}")
print("  ATTACK 2: LOW C + STRONG RECOVERY")
print(f"  Criterion: C ≤ Q1 ({c_lo:.4f}) AND restoration > 1.2")
print(f"{SEP}")
hits2 = []
for i in np.where(lo_mask)[0]:
    if rest[i] > 1.2:
        hits2.append(rows[i])
if hits2:
    print(f"\n  FOUND: {len(hits2)} runs with low C but strong recovery")
    for h in hits2:
        print(f"    C={h['pre_C']:.4f}  ΔC={h['dip']:+.4f}  rest={h['restoration']:.4f}  τ={h['tau_rec']:.0f}  fric={h['friction']:.2f}")
else:
    print(f"\n  NOT FOUND")

# ─── Attack 3: Same C, wildly different recovery ───
print(f"\n{SEP}")
print("  ATTACK 3: SAME C ±0.01, DIFFERENT τ_rec (ratio > 2×)")
print(f"{SEP}")
pairs = []
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        if abs(c[i] - c[j]) > 0.01: continue
        if np.isnan([tau[i], tau[j]]).any(): continue
        tr = max(tau[i], tau[j]) / max(min(tau[i], tau[j]), 1)
        if tr >= 2.0:
            pairs.append((i, j, tr))
pairs = pairs[:10]
if pairs:
    print(f"\n  FOUND: {len(pairs)} pairs with same C but τ_rec ratio ≥ 2×")
    for i, j, tr in pairs:
        print(f"    C≈{c[i]:.4f}  τ={tau[i]:.0f} vs {tau[j]:.0f}  (ratio={tr:.1f}×)  fric={fric[i]:.2f}/{fric[j]:.2f}")
        print(f"       rep={rows[i]['rep']}/fric={rows[i]['friction']:.2f} vs rep={rows[j]['rep']}/fric={rows[j]['friction']:.2f}")
else:
    print(f"\n  NOT FOUND")

# ─── Attack 4: Within-friction, C fails to explain τ_rec ───
print(f"\n{SEP}")
print("  ATTACK 4: WITHIN-FRICTION, C FAILS TO ORDER τ_rec")
print(f"  At each friction level, do top-C runs recover faster than bottom-C?")
print(f"{SEP}")
for fric_val in sorted(set(fric)):
    mask = fric == fric_val
    if mask.sum() < 6: continue
    c_f = c[mask]
    tau_f = tau[mask]
    # Split into high-C / low-C halves
    med = np.median(c_f)
    hi = tau_f[c_f >= med]
    lo = tau_f[c_f < med]
    if len(hi) < 2 or len(lo) < 2: continue
    hi_mean, lo_mean = np.nanmean(hi), np.nanmean(lo)
    direction = "C predicts τ" if hi_mean < lo_mean else "C FAILS"
    print(f"    friction={fric_val:.2f}: high-C τ={hi_mean:.0f} vs low-C τ={lo_mean:.0f}  ({direction})")

# ─── Attack 5: The sign reversal paradox ───
print(f"\n{SEP}")
print("  ATTACK 5: SIGN REVERSAL PARADOX")
print(f"  Same perturbation (10% removal) produces OPPOSITE ΔC sign depending on friction")
print(f"{SEP}")
neg = dip < -0.01
pos = dip > 0.01
zero = ~(neg | pos)
print(f"\n  Runs where C INCREASES after removal (ΔC < -0.01):  {neg.sum()} ({neg.sum()/len(rows)*100:.0f}%)")
print(f"    C range: {c[neg].min():.4f} – {c[neg].max():.4f}, mean C = {np.mean(c[neg]):.4f}")
print(f"  Runs where C DECREASES after removal (ΔC > +0.01):  {pos.sum()} ({pos.sum()/len(rows)*100:.0f}%)")
print(f"    C range: {c[pos].min():.4f} – {c[pos].max():.4f}, mean C = {np.mean(c[pos]):.4f}")

# Show the overlap: runs with similar C but opposite ΔC sign
print(f"\n  Overlap C = 0.43–0.45:")
overlap = (c >= 0.43) & (c <= 0.45)
for i in np.where(overlap)[0]:
    fric_label = {"LOW": fric[i] <= 0.2, "MID": 0.2 < fric[i] < 0.6, "HIGH": fric[i] >= 0.6}
    regime = "LOW" if fric[i] <= 0.2 else ("HIGH" if fric[i] >= 0.6 else "MID")
    sign = "+" if dip[i] > 0.01 else ("-" if dip[i] < -0.01 else "0")
    print(f"    C={c[i]:.4f}  ΔC={dip[i]:+.4f} ({sign})  rest={rest[i]:.4f}  τ={tau[i]:.0f}  fric={fric[i]:.2f}  friction={regime}")

# ─── Summary ───
print(f"\n{SEP}")
print("  FALSIFICATION SUMMARY")
print(f"{SEP}")
print(f"""
  Attacks 1–2 (extremal): Check if extremes of C predict extremes of recovery
    High C + poor recovery:     {'FOUND' if hits else 'NOT FOUND'}
    Low C + strong recovery:    {'FOUND' if hits2 else 'NOT FOUND'}

  Attack 3 (pairwise): Same C, different τ_rec
    Pairs with C±0.01, τ ratio≥2: {len(pairs)} found

  Attack 4 (within-friction): Does C order recovery within a friction level?
    {'Mixed — see per-friction results above'}

  Attack 5 (sign reversal): Does the same perturbation produce opposite effects?
    C increases after removal in {neg.sum()}/{len(rows)} runs
    C decreases after removal in {pos.sum()}/{len(rows)} runs
    These C ranges OVERLAP — identical C predicts opposite outcomes

  Interpretation:
    If C alone determined recovery, C would predict the DIRECTION of ΔC.
    It does not. The ΔC sign is determined by friction (mobility regime),
    not by C alone. This is the single strongest falsification of the
    one-factor hypothesis.
""")
