#!/usr/bin/env python3
"""RD-OSC.2D: Representation Robustness Audit

Tests whether the semantic similarity result survives representation change.
Methods: TF-IDF cosine, BM25, Character n-gram TF-IDF.
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import math

# Load data
with open('audits/rd_osc2b/coder_A_responses.json') as f:
    cA = json.load(f)
with open('audits/rd_osc2b/coder_B_responses.json') as f:
    cB = json.load(f)
with open('audits/rd_osc2b/coder_C_responses.json') as f:
    cC = json.load(f)
with open('audits/rd_osc2b/blind_packets_shuffled.json') as f:
    packets = json.load(f)

# Extract all 60 responses
responses = []
study_ids = []
for i in range(20):
    responses.append(cA[i]['what_changed'])
    study_ids.append(i)
    responses.append(cB[i]['what_changed'])
    study_ids.append(i)
    responses.append(cC[i]['what_changed'])
    study_ids.append(i)

def compute_within_between(sim_matrix, n_studies=20):
    """Extract within-study and between-study similarities."""
    within_sims = []
    for i in range(n_studies):
        idx_a = i * 3
        idx_b = i * 3 + 1
        idx_c = i * 3 + 2
        within_sims.append(sim_matrix[idx_a, idx_b])
        within_sims.append(sim_matrix[idx_a, idx_c])
        within_sims.append(sim_matrix[idx_b, idx_c])
    
    between_sims = []
    for i in range(n_studies):
        for j in range(i + 1, n_studies):
            for ci in range(3):
                for cj in range(3):
                    idx_i = i * 3 + ci
                    idx_j = j * 3 + cj
                    between_sims.append(sim_matrix[idx_i, idx_j])
    
    return np.array(within_sims), np.array(between_sims)

def permutation_test(within_sims, between_sims, sim_matrix, n_permutations=5000):
    """Permutation test for within > between."""
    observed_diff = within_sims.mean() - between_sims.mean()
    perm_diffs = []
    
    for _ in range(n_permutations):
        indices = list(range(60))
        np.random.shuffle(indices)
        
        perm_within = []
        for g in range(20):
            idx1 = indices[g * 3]
            idx2 = indices[g * 3 + 1]
            idx3 = indices[g * 3 + 2]
            perm_within.append(sim_matrix[idx1, idx2])
            perm_within.append(sim_matrix[idx1, idx3])
            perm_within.append(sim_matrix[idx2, idx3])
        
        perm_within = np.array(perm_within)
        perm_diffs.append(perm_within.mean() - between_sims.mean())
    
    perm_diffs = np.array(perm_diffs)
    p_value = (perm_diffs >= observed_diff).mean()
    return p_value, observed_diff, perm_diffs

def cohens_d(within, between):
    """Compute Cohen's d effect size."""
    pooled_std = np.sqrt((within.std()**2 + between.std()**2) / 2)
    if pooled_std == 0:
        return 0
    return (within.mean() - between.mean()) / pooled_std

results = {}

# Method 1: TF-IDF cosine (word-level)
print("=== Method 1: TF-IDF (word-level) ===")
vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
tfidf_matrix = vectorizer.fit_transform(responses)
sim_tfidf = cosine_similarity(tfidf_matrix)
within, between = compute_within_between(sim_tfidf)
p, diff, _ = permutation_test(within, between, sim_tfidf)
d = cohens_d(within, between)
print(f"  Within: {within.mean():.4f} ± {within.std():.4f}")
print(f"  Between: {between.mean():.4f} ± {between.std():.4f}")
print(f"  Cohen's d: {d:.4f}")
print(f"  p-value: {p:.6f}")
results['tfidf_word'] = {'within': within.mean(), 'between': between.mean(), 'd': d, 'p': p}

# Method 2: BM25 (Okapi BM25)
print("\n=== Method 2: BM25 ===")
# BM25 implementation
k1 = 1.5
b = 0.75

# Tokenize
tokenized = [r.lower().split() for r in responses]
# Compute IDF
doc_freq = Counter()
for doc in tokenized:
    for term in set(doc):
        doc_freq[term] += 1
n_docs = len(responses)
idf = {term: math.log((n_docs - df + 0.5) / (df + 0.5) + 1) for term, df in doc_freq.items()}

# Compute BM25 scores
def bm25_score(query_doc, doc):
    score = 0
    doc_len = len(doc)
    avg_dl = np.mean([len(d) for d in tokenized])
    tf = Counter(doc)
    for term in query_doc:
        if term in tf:
            term_tf = tf[term]
            term_idf = idf.get(term, 0)
            numerator = term_tf * (k1 + 1)
            denominator = term_tf + k1 * (1 - b + b * doc_len / avg_dl)
            score += term_idf * numerator / denominator
    return score

# Compute pairwise BM25 similarity matrix
sim_bm25 = np.zeros((60, 60))
for i in range(60):
    for j in range(60):
        sim_bm25[i, j] = bm25_score(tokenized[i], tokenized[j])

# Normalize to [0, 1]
if sim_bm25.max() > 0:
    sim_bm25 = sim_bm25 / sim_bm25.max()

within, between = compute_within_between(sim_bm25)
p, diff, _ = permutation_test(within, between, sim_bm25)
d = cohens_d(within, between)
print(f"  Within: {within.mean():.4f} ± {within.std():.4f}")
print(f"  Between: {between.mean():.4f} ± {between.std():.4f}")
print(f"  Cohen's d: {d:.4f}")
print(f"  p-value: {p:.6f}")
results['bm25'] = {'within': within.mean(), 'between': between.mean(), 'd': d, 'p': p}

# Method 3: Character n-gram TF-IDF
print("\n=== Method 3: Character n-gram TF-IDF ===")
vectorizer_ng = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=1000)
ng_matrix = vectorizer_ng.fit_transform(responses)
sim_ng = cosine_similarity(ng_matrix)
within, between = compute_within_between(sim_ng)
p, diff, _ = permutation_test(within, between, sim_ng)
d = cohens_d(within, between)
print(f"  Within: {within.mean():.4f} ± {within.std():.4f}")
print(f"  Between: {between.mean():.4f} ± {between.std():.4f}")
print(f"  Cohen's d: {d:.4f}")
print(f"  p-value: {p:.6f}")
results['char_ngram'] = {'within': within.mean(), 'between': between.mean(), 'd': d, 'p': p}

# Method 4: TF-IDF with bigrams
print("\n=== Method 4: TF-IDF (bigrams) ===")
vectorizer_bi = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=500)
bi_matrix = vectorizer_bi.fit_transform(responses)
sim_bi = cosine_similarity(bi_matrix)
within, between = compute_within_between(sim_bi)
p, diff, _ = permutation_test(within, between, sim_bi)
d = cohens_d(within, between)
print(f"  Within: {within.mean():.4f} ± {within.std():.4f}")
print(f"  Between: {between.mean():.4f} ± {between.std():.4f}")
print(f"  Cohen's d: {d:.4f}")
print(f"  p-value: {p:.6f}")
results['tfidf_bigram'] = {'within': within.mean(), 'between': between.mean(), 'd': d, 'p': p}

# Summary
print("\n=== SUMMARY ===")
print(f"{'Method':<20} {'Within':>10} {'Between':>10} {'Cohen d':>10} {'p-value':>10}")
print("-" * 60)
for method, r in results.items():
    print(f"{method:<20} {r['within']:>10.4f} {r['between']:>10.4f} {r['d']:>10.4f} {r['p']:>10.6f}")

# Rank consistency
methods = list(results.keys())
d_values = [results[m]['d'] for m in methods]
rank_order = sorted(range(len(d_values)), key=lambda i: d_values[i], reverse=True)
print(f"\nRank order by effect size: {[methods[i] for i in rank_order]}")
print(f"All p-values < 0.05: {all(results[m]['p'] < 0.05 for m in methods)}")
print(f"All Cohen's d > 0.8: {all(results[m]['d'] > 0.8 for m in methods)}")

# Save results
with open('audits/rd_osc2d/representation_robustness_results.json', 'w') as f:
    json.dump(results, f, indent=2)
