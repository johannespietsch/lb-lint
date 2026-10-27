# METRICS

Every row dated. Every change to a prompt or model gets a new dated row.
Early numbers are kept — they are the baseline.

## Definitions

| Metric | Defined as | From |
|---|---|---|
| Extraction span-F1 | IoU ≥ 0.5 against golden set | M2 |
| § 31(6) precision / recall | exact flag-set comparison | M2 |
| Determinism rate | fraction of 5 runs at T=0 with identical normalised finding sets | M2 |
| Offset-repair rate | share of quotes located only by whitespace-tolerant matching (D-008) | M1 |
| Offset-rejection rate | share of quotes not located at all (D-008) | M1 |
| Cost per document | EUR, mean over golden set | M1 |
| p95 latency | end-to-end, per document | M2 |
| Retrieval MRR@5 | 15 hand-written German queries; vector / FTS / hybrid | M3 |
| Cluster silhouette | at chosen k | M3 |
| Annotation self-agreement | re-annotation of excerpts 1–5 vs. originals | M2 |

## Runs

| Datum | Änderung | Provider:Modell | Anforderungen | Offset-Repair | Offset-Rejection | Tokens (in/out) | EUR | Wall time |
|---|---|---|---|---|---|---|---|---|
| 2026-10-27 | M1 baseline, extraction only (no rules yet); `samples/laptops_schulen.md`, 1 run | anthropic:claude-haiku-5-5, effort low | 34 | 0 | 0 | 11 232 / 2 660 | 0.002192 | 20.7 s |
| 2026-10-27 | M1 full pipeline (`make demo`), runs 2–3; 23 Befunde (3 LB101, 2 LB102, 3 LB201, 15 LB202) | anthropic:claude-haiku-5-5, effort low | 34 | 0 | 0 | 11 232 / 2 660 | 0.002192 | ≈ 20 s |

## Pricing basis

Costs in EUR are computed with fixed, dated inputs (`providers.py`), so a re-run gives the same number.

| Since | Model | USD / 1M input | USD / 1M output | Source |
|---|---|---|---|---|
| 2026-10-27 | claude-haiku-5-5 (≤ 100K-token prompts) | 0.10 | 0.50 | Claude API reference, as of 2026-10-06 |
| 2026-10-27 | claude-haiku-5-5 (> 100K-token prompts) | 0.50 | 2.50 | same |
| 2026-10-27 | claude-sonnet-5-5 | 2.00 | 10.00 | same |

Exchange rate: 1 EUR = 1.1188 USD (ECB reference rate, 2026-10-26).

## Observations

- 2026-10-27: three runs on the sample gave identical token counts (11 232 / 2 660) and 34 Anforderungen each. Suggestive for determinism, not evidence: one document, no comparison of the finding sets. M2 measures it properly.
- 2026-10-27: LB202 produces 15 of 23 findings, several of them noise (yes/no features; "höchstens einen Werktag" is measurable but written as a word, not a digit).
