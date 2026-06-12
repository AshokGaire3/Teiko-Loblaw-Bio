# Part 3: Statistical Analysis Report

Comparing cell population relative frequencies of melanoma patients receiving miraclib (PBMC samples only).

## Summary of Findings
- Analysis includes **Welch's t-test** (to evaluate differences in population means under unequal variances) and **Mann-Whitney U test** (a non-parametric test evaluating differences in distributions).
- Significance threshold set at $\alpha = 0.05$.

| Population | Responder Mean (SD) | Non-Responder Mean (SD) | t-test p-value | Mann-Whitney p-value | Significant? |
|---|---|---|---|---|---|
| B Cell | 9.798% (3.323%) | 9.996% (3.118%) | 0.171213 | 0.055702 | **Not Significant** |
| Cd8 T Cell | 24.882% (4.914%) | 24.944% (4.417%) | 0.768468 | 0.639086 | **Not Significant** |
| Cd4 T Cell | 30.538% (5.208%) | 29.902% (4.824%) | 0.005013 | 0.013344 | **Significant** |
| Nk Cell | 14.841% (4.132%) | 15.073% (3.767%) | 0.192649 | 0.121051 | **Not Significant** |
| Monocyte | 19.942% (4.642%) | 20.084% (4.011%) | 0.465844 | 0.163150 | **Not Significant** |

## Conclusions
- **CD4+ T-cell relative frequency** is the only cell type that shows a statistically significant difference between responders and non-responders (Welch's t-test p = 0.0050, Mann-Whitney U test p = 0.0133).
- Responders show a slightly higher proportion of CD4+ T-cells (mean of 30.54% vs 29.90%).
- Other immune cell populations (B-cells, CD8+ T-cells, NK cells, and monocytes) do not display significant differences under either parametric or non-parametric metrics. Thus, baseline and longitudinal CD4+ T-cell profiles might be a key indicator of therapeutic response to **miraclib**.
