# Known limitations

What lb-lint does not do, or does imperfectly, as of 2026-10-27. Each item links to the decision or incident that explains it. lb-lint is a linter, not legal advice: every finding is a proposal for a human to accept or reject.

## Legal scope

- **Above-threshold (VgV) procurement only.** Below the EU thresholds, § 23 Abs. 5 UVgO allows dropping "oder gleichwertig" for a documented reason, so some LB101 errors are wrong there. ([D-006](DECISIONS.md))
- **Brand and product-type references only.** References to origin ("aus europäischer Fertigung") or to a specific process are not detected, although § 31 Abs. 6 VgV covers them. ([D-007](DECISIONS.md))
- **Norm references without "oder gleichwertig" are not checked** (§ 31 Abs. 2 VgV). ([D-007](DECISIONS.md))
- **Eco labels and quality marks are not checked** (TCO Certified, Blauer Engel; § 34 VgV).
- **LB102 cannot judge whether a brand reference is justified.** It only reminds the reviewer to check and document the justification. ([D-007](DECISIONS.md))
- **The legal rule choices are provisional.** They were made without a procurement practitioner. Treating "oder vergleichbar" as equivalent to "oder gleichwertig" rests on a single tribunal decision. ([D-007](DECISIONS.md))

## Rule precision

- **LB202 (`fehlende-messgroesse`) is noisy.** It flags any requirement without a digit or a norm reference. That catches yes/no features ("spritzwassergeschützt") and quantities written as words ("höchstens einen Werktag"). On the sample it produced 15 of 23 findings. It is kept as a `hinweis` until M2 measures its precision. ([D-012](DECISIONS.md), [METRICS.md](METRICS.md))
- **Gazetteer false positives.** Bare "Office" and "Windows" match in non-product contexts, e.g. "Back-Office" in an address. A context check is planned for M4.
- **Gazetteer coverage.** About 60 IT brands and product types. Other sectors, spelling variants and a brand split across a line break are not matched. ([D-013](DECISIONS.md))
- **Vague-wording lexicon is small.** Six terms (`ausreichend`, `angemessen`, `zeitnah`, `marktüblich`, `hochwertig`, `nach Bedarf`). "Hohe Farbtreue" or "robust" only surface through LB202. ([D-012](DECISIONS.md))

## Segmentation

- **A sentence ending in a number followed by a capitalised word is not split** ("bis 2027. Danach …"), so the window for the "oder gleichwertig" check is too wide there. This is the price of not splitting German ordinals ("der 13. Generation"). ([D-011](DECISIONS.md))
- **Section numbers are positional,** not parsed from headings. Setext headings (`===`) and headings inside code blocks are not recognised. ([D-009](DECISIONS.md))
- **Input is `.md` / `.txt` only.** No PDF or DOCX. ([PLAN.md](PLAN.md), non-goal 1)

## Extraction

- **One requirement per bullet or sentence.** Compound bullets are not split. Borderline items (scope statements, permissions such as "Teillieferungen sind … zulässig") are sometimes extracted.
- **The zero offset-rejection rate so far comes from one document.** It is not yet evidence of verbatim quoting. ([METRICS.md](METRICS.md))

## Provider, cost and reproducibility

- **Currently runs on Anthropic, not the EU-hosted target provider.** The EU data-residency property is designed, not running. Do not process real procurement documents yet. ([D-010](DECISIONS.md))
- **No temperature control.** The Anthropic API no longer accepts sampling parameters, so model output is reproducible only as far as default sampling allows. Rule verdicts are deterministic regardless. ([I-002](INCIDENTS.md))
- **Determinism is not yet measured.** Three identical runs on one document are suggestive, not evidence. Measuring it is M2's job.
- **Costs use a fixed price table** (Claude API reference, 2026-10-06) and a fixed exchange rate (ECB, 2026-10-26). They are reproducible but will drift from actual invoices. ([METRICS.md](METRICS.md))
