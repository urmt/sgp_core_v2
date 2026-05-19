import numpy as np
import json
from pathlib import Path
from scipy.signal import hilbert
from scipy.stats import entropy

np.random.seed(42)

OUTPUT_DIR = Path("/home/student/sgp_core_v2/outputs/adversarial_optimization")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

N = 4000
ATTACK_STEPS = 500
NUM_ATTACKS = 25

def generate_evolving(n):
    t = np.linspace(0, 1, n)
    chirp = np.sin(2*np.pi*(3*t + 10*t**2))
    trend = 0.5 * t
    rw = np.cumsum(np.random.randn(n)) * 0.01
    return chirp + trend + rw

def replay_signal(x):
    return np.tile(x[:len(x)//4], 4)

def stitched_signal(x):
    chunks = np.array_split(x, 8)
    np.random.shuffle(chunks)
    return np.concatenate(chunks)

def reverse_signal(x):
    return x[::-1]

def amplified_temporal_mass(x):
    dx = np.gradient(x)
    w = np.linspace(1, 10, len(x))**2
    return float(np.sum(np.abs(dx) * w))

def directional_ngram_irreversibility(x, bins=8, ngram=3):
    q = np.digitize(x, np.histogram(x, bins=bins)[1][:-1])
    def grams(seq):
        return list(zip(*[seq[i:] for i in range(ngram)]))
    fwd = grams(q)
    rev = grams(q[::-1])
    vocab = list(set(fwd + rev))
    pf = np.array([fwd.count(v)+1 for v in vocab], dtype=float)
    pr = np.array([rev.count(v)+1 for v in vocab], dtype=float)
    pf /= pf.sum()
    pr /= pr.sum()
    return float(entropy(pf, pr))

def oriented_phase_area(x):
    analytic = hilbert(x)
    phase = np.unwrap(np.angle(analytic))
    amp = np.abs(analytic)
    return float(np.mean(np.gradient(phase) * amp))

def directional_lz_complexity_gradient(x):
    binary = (x > np.median(x)).astype(int)
    def lz(seq):
        s = ''.join(map(str, seq))
        i, c, l = 0, 1, 1
        while True:
            if i + l > len(s): return c
            sub = s[i:i+l]
            prev = s[:i]
            if sub in prev: l += 1
            else: c += 1; i += l; l = 1
    early = lz(binary[:len(binary)//2])
    late = lz(binary[len(binary)//2:])
    return float(late - early)

METRICS = {"mass": amplified_temporal_mass, "ngram": directional_ngram_irreversibility, "phase": oriented_phase_area, "lz": directional_lz_complexity_gradient}

def metric_vector(x):
    return np.array([fn(x) for fn in METRICS.values()], dtype=float)

def generate_adversary(target_signal, target_vector):
    best = None
    best_dist = np.inf
    current = np.random.permutation(target_signal)
    cur_vec = metric_vector(current)
    for step in range(ATTACK_STEPS):
        proposal = current.copy()
        i = np.random.randint(0, len(proposal)-64)
        j = np.random.randint(0, len(proposal)-64)
        block = proposal[i:i+64].copy()
        proposal[i:i+64] = proposal[j:j+64]
        proposal[j:j+64] = block
        if np.random.rand() < 0.2:
            k = np.random.randint(0, len(proposal)-256)
            proposal[k:k+256] = proposal[k:k+256][::-1]
        vec = metric_vector(proposal)
        dist = float(np.linalg.norm(vec - target_vector))
        if dist < best_dist:
            best_dist = dist
            best = proposal.copy()
        cur_dist = float(np.linalg.norm(cur_vec - target_vector))
        if dist < cur_dist:
            current = proposal
            cur_vec = vec
    return best, best_dist

evolving = generate_evolving(N)
replay = replay_signal(evolving)
stitched = stitched_signal(evolving)
reverse = reverse_signal(evolving)

evo_vec = metric_vector(evolving)
rep_vec = metric_vector(replay)
sti_vec = metric_vector(stitched)
rev_vec = metric_vector(reverse)

attack_distances = []
for k in range(NUM_ATTACKS):
    print(f"  Attack {k+1}/{NUM_ATTACKS}...", flush=True)
    adv_sig, adv_dist = generate_adversary(evolving, evo_vec)
    attack_distances.append(adv_dist)
    print(f"    done: min_dist={adv_dist:.4f}", flush=True)

min_adv_distance = float(np.min(attack_distances))
mean_adv_distance = float(np.mean(attack_distances))

replay_distance = float(np.linalg.norm(evo_vec - rep_vec))
stitched_distance = float(np.linalg.norm(evo_vec - sti_vec))
reverse_distance = float(np.linalg.norm(evo_vec - rev_vec))

metric_matrix = np.array([evo_vec, rep_vec, sti_vec, rev_vec])
corr = np.corrcoef(metric_matrix.T)
max_corr = float(np.max(np.abs(corr[np.triu_indices_from(corr, k=1)])))

gate_open = bool(
    replay_distance > 0.20 and
    stitched_distance > 0.25 and
    reverse_distance > 0.40 and
    min_adv_distance > 0.20 and
    max_corr < 0.90
)

results = {
    "replay_distance": replay_distance,
    "stitched_distance": stitched_distance,
    "reverse_distance": reverse_distance,
    "min_adversarial_distance": min_adv_distance,
    "mean_adversarial_distance": mean_adv_distance,
    "max_metric_corr": max_corr,
    "gate_open": gate_open,
    "attack_distances": attack_distances,
    "correlation_matrix": corr.tolist()
}

outpath = OUTPUT_DIR / "v2_051_results.json"
with open(outpath, "w") as f:
    json.dump(results, f, indent=2)

print("\nV2_051 ADVERSARIAL OPTIMIZATION AUDIT\n")
print(f"Replay distance:       {replay_distance:.3f}")
print(f"Stitched distance:    {stitched_distance:.3f}")
print(f"Reverse distance:     {reverse_distance:.3f}")
print(f"\nMin adversarial dist: {min_adv_distance:.3f}")
print(f"Mean adversarial dist: {mean_adv_distance:.3f}")
print(f"\nMax correlation:      {max_corr:.3f}")
print(f"\nGATE OPEN: {gate_open}")
print(f"\nSaved to: {outpath}")
