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
**Fix:** Open — decided with the sentence window for the rule checks (M1 step 7). Sections are split by heading only (D-009), so extraction is unaffected.
**Wie hätte es auffallen müssen:** Exactly this way: by testing the segmenter on the sample before trusting it. The cases above become regression tests in step 7.
**Im Mehrmandantenbetrieb:** A rule window that silently spans two sentences can pick up "oder gleichwertig" from the neighbouring sentence — a false negative on a legal check, for every tenant at once. Statistical boundaries can also change with a model upgrade, which is why the model version is pinned (`make setup`).
