# DECISIONS

<!--
## D-00N — <the decision, in one line>
**Datum:** YYYY-MM-DD  **Status:** entschieden | revidiert durch D-00M

**Kontext:** what forced a choice here at all.
**Entscheidung:** what was done.
**Verworfene Alternative(n):** what was not done, and the concrete cost
that ruled it out — not "seemed worse."
**Konsequenz:** what this now makes easy, and what it makes expensive later.
-->

## D-001 — Mistral (EU-hosted) as primary LLM provider
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** Every draft sent to an LLM crosses the data-residency boundary (T2). Public-sector documents come with data-residency expectations, so the provider choice is a compliance decision before it is a quality one.
**Entscheidung:** Mistral (EU-hosted) is the primary provider. All calls go through a single chokepoint (`providers.py`), so swapping providers is a config change. Anthropic stays behind a flag for eval comparison only.
**Verworfene Alternative(n):** Anthropic/OpenAI as primary for raw capability — rejected because it would send tender drafts outside the EU by default, which is the first question a contracting authority asks.
**Konsequenz:** "Where does our data go?" has one concrete answer. The quality cost of the EU choice is measured on the golden set rather than assumed; if the gap turns out large, that is a number to argue with, not a feeling.

## D-002 — Character offsets are mandatory on every extracted requirement
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** A finding has to be verifiable against the source document, otherwise *revisionssicher* is a claim rather than a property.
**Entscheidung:** Every `Anforderung` carries `(start, end)` into the source; the returned text is validated against `source[start:end]` and repaired or rejected on mismatch.
**Verworfene Alternative(n):** Return requirement text only — rejected because text alone cannot be located unambiguously in the source, so no finding could be clicked through to or audited.
**Konsequenz:** Findings are clickable and auditable. Cost: a more complex prompt and a validate-and-repair step; the rejection rate becomes a tracked metric of model reliability.

## D-003 — Legally load-bearing checks are deterministic code, not LLM judgements
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** Anything carrying a `rechtsgrundlage` must give the same answer twice. A model does not.
**Entscheidung:** § 31 Abs. 6 VgV and § 121 Abs. 1 GWB checks are rules in code (gazetteer, lexicon). The LLM's role is *extraction and context*; the rules' role is *verdict*.
**Verworfene Alternative(n):** Ask the model "ist diese Anforderung produktneutral?" — rejected because its answer is not reproducible and cannot be defended in a Nachprüfungsverfahren.
**Konsequenz:** Verdicts are reproducible and unit-testable without an API key. Rules will have false positives (e.g. "Windows" meaning *Fenster*) that only context can resolve — that is the critique node's job later, and it may only add advisory context, never override a rule.

## D-004 — Rule IDs: short code plus readable name
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** Every finding needs a rule identifier that people can cite, suppress, and filter on, the way linter users cite `E501`.
**Entscheidung:** Each rule has a short code and a kebab-case name, e.g. `LB101 produktneutralitaet-verletzt`, `LB201 vage-formulierung`. The hundreds digit groups rules by legal provision (1xx Produktneutralität, 2xx Eindeutigkeit).
**Verworfene Alternative(n):** Long names only (`PRODUKTNEUTRALITAET_VERLETZT`) — readable, but long to cite, and they give no grouping by provision, so filtering "all § 31 rules" needs a separate mapping.
**Konsequenz:** Findings can be filtered by provision via the code prefix, and the name keeps output readable. Codes must never be reused once published, otherwise old audit records change meaning.

## D-005 — Two identifiers per Anforderung: stable hash `id` + readable `label`
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** Requirements are referenced by people (in the review UI, in discussion) and by stored data (accept/reject decisions from M5, caches, eval diffs). A positional ID like `A-3-2` shifts when a requirement is inserted earlier in the section, so stored decisions would silently attach to the wrong requirement on a re-check of a revised draft.
**Entscheidung:** `id` is a content hash: the first 12 hex characters of `sha256` over the whitespace-normalised requirement text, with an occurrence index appended when identical text appears more than once in a document. `label` is `A-<abschnitt>-<n>` for display only. Anything persisted references `id`; anything shown to a person uses `label`.
**Verworfene Alternative(n):** `A-<abschnitt>-<n>` alone — readable, but unstable across document revisions. Hash alone — stable, but unusable in conversation ("the requirement 3f9a…").
**Konsequenz:** Human decisions survive edits elsewhere in the document. Editing a requirement's own text gives it a new `id`, which is intended: an accepted finding on the old wording should not carry over to new wording. Cost: one more field, and the rule "persist `id`, display `label`" has to be kept consistently.

## D-006 — M1 checks against the VgV regime only (above EU thresholds)
**Datum:** 2026-10-26  **Status:** entschieden

**Kontext:** The same sentence can get different verdicts depending on regime. Above the EU thresholds, § 31 Abs. 6 VgV always requires "oder gleichwertig" on a permitted product reference. Below them, § 23 Abs. 5 UVgO allows dropping it when a documented sachlicher Grund exists (e.g. compatibility with existing equipment). See `notes/reading.md`.
**Entscheidung:** M1 assumes the VgV regime. Rules cite § 31 VgV and § 121 GWB. The sample document is written as an EU-wide procurement.
**Verworfene Alternative(n):** UVgO only — more realistic for municipal buyers, but the rule needs to detect a documented justification, which is not a pattern match. A per-run `regime` input — the correct end state, but it changes the `Befund` model and doubles the rule test matrix before a single rule works.
**Konsequenz:** Rules stay simple and the legal basis is unambiguous. **Known gap:** below-threshold procurement, the most common municipal case, is not covered, and the TED corpus (M3) has the same blind spot. Adding a `regime` input later means every rule's `rechtsgrundlage` becomes regime-dependent.

## D-007 — Scope of the § 31 Abs. 6 VgV rule for M1
**Datum:** 2026-10-26  **Status:** vorläufig — set without domain expertise, to be reviewed with a procurement practitioner

**Kontext:** The statute is broader than a brand list can check (see `notes/reading.md`, Q2–Q5). Four scope questions had to be settled before writing the rule.
**Entscheidung:**
1. A brand/type reference **with** the addition still gets severity `hinweis` ("Begründung prüfen"). The addition is necessary but not sufficient: the reference must also be justified by the subject matter, which a rule cannot see.
2. "oder vergleichbar" counts as the addition, like "oder gleichwertig". Supported by VK Mecklenburg-Vorpommern, Beschl. v. 29.11.2021, 2 VK 4/21 (VOB/A context, cited in [iww.de](https://www.iww.de/pbp/vob/voba-leitfabrikat-oder-gleichwertig-auftraggeber-darf-so-ausschreiben-bieter-aber-nicht-bieten-f156066); full text not checked). "Oder gleichwertig" remains the statutory and usual wording.
3. Origin (*Herkunft, Ursprung*) and process references are out of scope; only brands and product types from the gazetteer are checked.
4. No rule for norm references without "oder gleichwertig" (§ 31 Abs. 2 VgV).
**Verworfene Alternative(n):** Covering all of § 31 Abs. 6 and Abs. 2 in M1 — legally more complete, but origin and process references need semantic detection, not a gazetteer, and the extra scope would not change the demo.
**Konsequenz:** One gazetteer rule with two severities. **Known false negatives:** origin requirements ("aus europäischer Fertigung") and bare norm references, both of which appear in `samples/laptops_schulen.md`. If a client or practitioner rejects item 2, the fix is a one-word change in the rule plus a new eval run.
