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
