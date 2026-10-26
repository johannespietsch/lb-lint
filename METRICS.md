# METRICS

Every row dated. Every change to a prompt or model gets a new dated row.
Early numbers are kept — they are the baseline.

## Definitions

| Metric | Defined as | From |
|---|---|---|
| Extraction span-F1 | IoU ≥ 0.5 against golden set | M2 |
| § 31(6) precision / recall | exact flag-set comparison | M2 |
| Determinism rate | fraction of 5 runs at T=0 with identical normalised finding sets | M2 |
| Offset-rejection rate | share of extracted spans failing verbatim validation | M1 |
| Cost per document | EUR, mean over golden set | M1 |
| p95 latency | end-to-end, per document | M2 |
| Retrieval MRR@5 | 15 hand-written German queries; vector / FTS / hybrid | M3 |
| Cluster silhouette | at chosen k | M3 |
| Annotation self-agreement | re-annotation of excerpts 1–5 vs. originals | M2 |

## Runs

| Datum | Änderung | Modell | Anforderungen | Offset-Rejection | Tokens (in/out) | EUR | Wall time |
|---|---|---|---|---|---|---|---|
