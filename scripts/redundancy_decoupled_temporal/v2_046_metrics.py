import numpy as np
from collections import Counter

def amplified_temporal_mass(x):
    dx = np.diff(x)
    ddx = np.diff(dx)
    pos = np.linspace(0, 1, len(ddx))
    weights = (pos**4) * np.exp(4*pos)
    return float(np.sum(np.abs(ddx) * weights))

def directional_ngram_irreversibility(x, bins=8, n=5):
    qs = np.quantile(x, np.linspace(0,1,bins+1)[1:-1])
    sym = np.digitize(x, qs)
    def ngrams(seq):
        return [tuple(seq[i:i+n]) for i in range(len(seq)-n)]
    fwd = Counter(ngrams(sym))
    rev = Counter(ngrams(sym[::-1]))
    keys = set(fwd.keys()) | set(rev.keys())
    diff = 0.0
    for k in keys:
        diff += abs(fwd.get(k,0) - rev.get(k,0))
    return float(diff / (len(sym) + 1e-9))

def oriented_phase_area(x, tau=8):
    x1 = x[:-tau]
    x2 = x[tau:]
    area = 0.0
    for i in range(len(x1)-1):
        area += (x1[i]*x2[i+1] - x2[i]*x1[i+1])
    return float(area / len(x1))

def lz_complexity(bits):
    i = 0
    c = 1
    seen = set()
    while i < len(bits)-1:
        for j in range(i+1, len(bits)+1):
            s = tuple(bits[i:j])
            if s not in seen:
                seen.add(s)
                c += 1
                i = j
                break
        else:
            break
    return c

def directional_lz_complexity_gradient(x):
    med = np.median(x)
    bits = (x > med).astype(int)
    thirds = np.array_split(bits, 3)
    vals = []
    for seg in thirds:
        vals.append(lz_complexity(seg))
    return float(vals[-1] - vals[0])
