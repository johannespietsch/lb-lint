# INCIDENTS

<!--
## I-00N — <one-line symptom>
**Datum:** YYYY-MM-DD  **Gefunden durch:** test | eval | zufällig | Nutzer

**Symptom:** what was actually observed, before it was understood.
**Erste Hypothese:** what it was thought to be. Keep this even when wrong —
  especially when wrong.
**Tatsächliche Ursache:** what it was.
**Fix:** what changed.
**Wie hätte es auffallen müssen:** the test, metric, or alert that would have
  caught it earlier — and whether it was then added.
**Im Mehrmandantenbetrieb:** what this failure mode would cost with many
  tenants in production, and what would prevent it there.
-->

## I-001 — Sentence boundaries around statute citations depend on the statistical parser
**Datum:** 2026-10-26  **Gefunden durch:** test (exploration before writing the rule engine)

**Symptom:** The predicted problem (PLAN.md, M1 trap: "Abs." and "z. B." shredding sentences) does not occur with `de_core_news_lg` 3.8.0. Instead, boundaries *around* citations are unreliable: "… gemäß § 57 Abs. 1 VgV. Danach folgt …" splits into `"… Abs. 1"`, `"VgV."`, `"Danach …"`, while "Es gilt § 31 Abs. 6 VgV. Die Geräte …" splits correctly. "… Abs. 1 VgV. Ende." is not split at all. The parser also ignores Markdown structure: it detaches `##` from its heading and merges two adjacent bullets into one sentence.
**Erste Hypothese:** Over-splitting at German abbreviations, fixable with tokenizer exceptions (the plan's prediction).
**Tatsächliche Ursache:** spaCy 3.8's German tokenizer exceptions already cover `Abs.`, `Nr.`, `z. B.`, `i. V. m.`, `ggf.`, `inkl.`. But `VgV.` at the end of a sentence is tokenised as one abbreviation-like token, so the full stop is absorbed and whether a boundary follows is left to the dependency parser — a statistical guess. The rule-based `sentencizer` respects bullet lines better but makes the same `VgV.` error.
**Fix:** spaCy is not used for sentence windows at all. `rules/saetze.py` (D-011) splits by fixed rules and treats a full stop after `VgV`/`GWB` as a sentence end. Sections are split by heading only (D-009), so extraction was never affected.
**Wie hätte es auffallen müssen:** Exactly this way: by testing the segmenter on the sample before trusting it. The cases above are regression tests in `tests/test_saetze.py`.
**Im Mehrmandantenbetrieb:** A rule window that silently spans two sentences can pick up "oder gleichwertig" from the neighbouring sentence — a false negative on a legal check, for every tenant at once. Statistical boundaries can also change with a model upgrade, which is why the model version is pinned (`make setup`).

## I-002 — "Temperature 0" no longer exists on the Anthropic API
**Datum:** 2026-10-27  **Gefunden durch:** zufällig (API reference read while writing `providers.py`)

**Symptom:** PLAN.md measures determinism "over 5 runs at temperature 0" and the audit record has a `temperature` field. Since API version 2026-10-21, any Messages request carrying `temperature`, `top_p` or `top_k` is rejected with a 400 on every Claude model. pydantic-ai 2.61 drops these settings silently for such models, so code setting `temperature=0` would run and the audit record would claim a setting that was never sent.
**Erste Hypothese:** none — the plan's assumption was simply never checked against the current API.
**Tatsächliche Ursache:** The plan was written against an older API surface.
**Fix:** `LlmAufruf.temperature` is optional and recorded only when the provider actually accepted it. The settings that do apply (`effort`, `thinking`) are recorded instead. Determinism in M2 is measured at the provider's default sampling, and reported as such.
**Wie hätte es auffallen müssen:** By checking every sampling assumption against the provider's current docs when writing the provider module. A test asserts the audit record never contains a temperature for an Anthropic call.
**Im Mehrmandantenbetrieb:** An audit record stating a setting that was never applied is worse than no record: it is a false statement in exactly the document a Vergabekammer would read. Record what was sent, never what was configured.
