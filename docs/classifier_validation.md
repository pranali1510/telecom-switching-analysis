# Classifier validation

Hand-labelled sample: 150 complaint reviews (random sample, labelled blind: predictions hidden).
Overall accuracy: 56.7%

| Theme | Labelled count | Precision | Recall |
|---|---|---|---|
| App Performance & Bugs | 51 | 66% | 57% |
| Billing & Pricing | 23 | 47% | 65% |
| Customer Support | 19 | 57% | 21% |
| Network & Connectivity | 44 | 68% | 64% |
| Other complaint | 13 | 35% | 69% |
## label_sample_round2.csv (rules v2, scored 2026-10-16)

Sample: 100 complaint reviews, random, labelled blind (predictions hidden).
Overall accuracy: 71.0% (95% interval 61% to 79%)
Note: a score on a sample that was used to tune the rules is optimistic; only a fresh blind sample is a fair test.

| Theme | Labelled count | Precision | Recall |
|---|---|---|---|
| App Performance & Bugs | 47 | 97% | 68% |
| Billing & Pricing | 12 | 59% | 83% |
| Customer Support | 6 | 20% | 33% |
| Network & Connectivity | 25 | 74% | 80% |
| Other complaint | 10 | 54% | 70% |

