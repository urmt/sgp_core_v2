# Mathematical Definition

## Coherence

Let \(X = \{X_1, \ldots, X_n\}\) be a set of \(n\) random variables (components), each with marginal distribution \(P_i\) and joint distribution \(P\).

### Marginal Entropy

\[
H(X_i) = -\int P_i(x) \log P_i(x) \, dx
\]

### Joint Entropy

\[
H(X_1, \ldots, X_n) = -\int P(x_1, \ldots, x_n) \log P(x_1, \ldots, x_n) \, dx_1 \ldots dx_n
\]

### Total Correlation (Watanabe 1960)

\[
T(X_1, \ldots, X_n) = \sum_i H(X_i) - H(X_1, \ldots, X_n)
\]

Properties:
- \(T \geq 0\) (non-negative)
- \(T = 0\) iff all \(X_i\) are independent
- \(T\) is invariant under permutation of variables

### Coherence

\[
C = \frac{T}{T + \sum_i H_i}
\]

Properties:
- \(C \in [0, 1]\)
- \(C = 0\) iff all variables are independent (\(T = 0\))
- \(C = 1\) iff total correlation dominates all marginal entropy
- Invariant under joint scaling of all variables
- Not invariant under variable-wise scaling

## Estimation

### Density Estimation

For a sample \(\{x^{(1)}, \ldots, x^{(m)}\}\):

\[
\hat{P}(x) = \frac{1}{m} \sum_{j=1}^m K(x - x^{(j)})
\]

where \(K\) is a Gaussian kernel with bandwidth \(h\) selected by Scott's rule:

\[
h = m^{-1/(d+4)}
\]

where \(d\) is the number of dimensions.

### Sampling

Entropy is estimated by evaluating \(\hat{P}\) at each sample point and computing the mean log-density. This produces a consistent but biased estimate. Bias is proportional to \(1/m\) and decreases with sample size.

## References

- Watanabe, S. (1960). Information theoretical analysis of multivariate correlation. *IBM Journal of Research and Development*, 4(1), 66–82.
- Scott, D. W. (2015). *Multivariate Density Estimation: Theory, Practice, and Visualization* (2nd ed.). Wiley.
