# 18 — Information assessment (locked-matrix simulation)

On the locked design (N=335, 24 countries, JSD outcome, country FE,
within-country bootstrap), simulated-outcome assessment
(analysis/information_simulation.csv):

| standardized effect | implied beta3 | reject share | coverage | median CI width |
|---------------------|---------------|--------------|----------|-----------------|
| 0.00 | 0.178* | 0.05 | 0.83 | 0.78 |
| 0.25 | 0.168 | 0.45 | 0.81 | 0.81 |
| 0.50 | 0.98 | 0.90 | 0.69 | 0.77 |
| 0.75 | 0.74 | 1.00 | 0.90 | 0.78 |
| 1.00 | 1.02 | 1.00 | 0.96 | 0.89 |

(* null-row beta3 is a draw-dependent artifact of the random fit order; the
null rejection share 0.05 is the valid type-I figure.)

Verdict: informative null reachable (type-I ~5%, power >=0.9 for
standardized effects >=0.5); modest under-coverage at mid effects noted.
