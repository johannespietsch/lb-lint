# lb-lint

**Ein Linter für Leistungsbeschreibungen**: a linter for German public tender specifications.

> **lb-lint is a linter, not legal advice.** It flags patterns against two named provisions of German procurement law (§ 31 Abs. 6 VgV, § 121 Abs. 1 GWB). Every finding is a proposal for a human to accept or reject. It does not replace review by a procurement lawyer. The legal rule choices are provisional and have not yet been reviewed by a practitioner; see [LIMITATIONS.md](LIMITATIONS.md).

**Status:** proof of concept (milestone M1 of [PLAN.md](PLAN.md)). It runs end to end on Markdown input. The evaluation harness (M2) is not built yet, so there are no quality numbers yet.

---

## The problem

Public tender documents have to be *revisionssicher*: traceable, reproducible, defensible. If a Leistungsbeschreibung is challenged before a Vergabekammer, the contracting authority must be able to say which sentence came from where, and on what basis. A language model offers none of that by default.

Two formal defects are common in drafts and can be checked by machine:

- **Produktneutralität (§ 31 Abs. 6 VgV).** A specification must not name a particular make, type or origin unless that is justified and the reference carries *"oder gleichwertig"*.
- **Eindeutigkeit (§ 121 Abs. 1 GWB).** The subject matter must be described *"so eindeutig wie möglich"*. "Ausreichende Akkulaufzeit" is not a requirement; it is a future dispute.

lb-lint sits between whatever *drafted* a Leistungsbeschreibung (a person, a template or an LLM) and the person who *signs* it. Think `ruff`, but for tender specifications: every finding has a rule ID, a character span in the source, a legal basis, and an audit record.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and an Anthropic API key.

```bash
make setup                                     # uv sync
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
make demo                                      # checks samples/laptops_schulen.md
make test                                      # 42 tests, no API key needed
```

```bash
uv run lb-lint pruefe path/to/leistungsbeschreibung.md          # table of findings
uv run lb-lint pruefe path/to/leistungsbeschreibung.md --json   # Anforderungen + Befunde as JSON
```

Every run writes `pruefprotokoll.json`, the audit record. Like a linter, the command exits with code 1 if there is at least one finding of severity `fehler`.

Example output on the included sample (abridged):

```
           laptops_schulen.md: 34 Anforderungen, 23 Befunde
 Anforderung  Regel                                   Schwere  Zitat              Rechtsgrundlage
 A-2-1        LB101 produktneutralitaet-verletzt      fehler   Intel Core i5      § 31 Abs. 6 VgV
 A-2-7        LB201 vage-formulierung                 warnung  ausreichende       § 121 Abs. 1 GWB
 A-4-1        LB102 produktneutralitaet-begruendung…  hinweis  Microsoft Windows  § 31 Abs. 6 VgV
 A-4-3        LB101 produktneutralitaet-verletzt      fehler   Microsoft Office   § 31 Abs. 6 VgV
 A-5-3        LB201 vage-formulierung                 warnung  zeitnah            § 121 Abs. 1 GWB
 …
Prüfprotokoll: pruefprotokoll.json · claude-haiku-5-5 · 11232/2660 Tokens · 0.002192 EUR
```

The sample document and its planted defects are in [`samples/`](samples/).

## How it works

```
draft (.md) ──► segment ──► extract ──► locate ──► rules ──► findings + audit record
               by heading    LLM         code       code
                             quotes      computes   decides
                             verbatim    offsets    verdicts
```

1. **Segment.** The document is split into sections (*Abschnitte*) by Markdown heading. Sections are the LLM's unit of work.
2. **Extract.** The LLM returns each requirement (*Anforderung*) as a verbatim quote, plus a category. It returns no positions and no IDs.
3. **Locate.** Code finds each quote in the source and computes its exact character span. A quote that cannot be found is rejected and counted, so paraphrasing is measured rather than hidden.
4. **Rules.** Deterministic checks scan the source with a rule-based sentence splitter. Each finding (*Befund*) is attached to the requirement that contains it.

| Rule | Severity | Legal basis | Flags |
|---|---|---|---|
| `LB101 produktneutralitaet-verletzt` | fehler | § 31 Abs. 6 VgV | Brand or product type without "oder gleichwertig" / "oder vergleichbar" in the same sentence |
| `LB102 produktneutralitaet-begruendung-pruefen` | hinweis | § 31 Abs. 6 VgV | Brand or product type *with* the addition: allowed only if justified, so check and document why |
| `LB201 vage-formulierung` | warnung | § 121 Abs. 1 GWB | Vague terms: *ausreichend, angemessen, zeitnah, marktüblich, hochwertig, nach Bedarf* |
| `LB202 fehlende-messgroesse` | hinweis | § 121 Abs. 1 GWB | Requirement with neither a number nor a norm reference (noisy; see limitations) |

### Design principles

- **The LLM reads; rules decide.** Language understanding sits with the LLM: extraction, later advisory context. Every finding that carries a legal basis comes from deterministic code, so the same document gets the same verdict twice. ([D-003](DECISIONS.md))
- **No statistical model in the verdict path.** The plan used spaCy's German model for sentence splitting. Testing showed its boundaries around statute citations ("… VgV. Danach …") are statistical guesses. It was replaced by fixed rules and regular expressions, which also cut setup from a 560 MB download to `uv sync`. ([D-013](DECISIONS.md), [I-001](INCIDENTS.md))
- **Code computes offsets, not the model.** LLMs are bad at counting characters, so the model only quotes and code locates the quote. ([D-008](DECISIONS.md))
- **The audit record states only what was actually sent.** The Anthropic API no longer accepts `temperature`, so the record does not claim one. ([I-002](INCIDENTS.md))
- **Untrusted input stays data.** Draft text is passed to the model inside a delimited block, never interpolated into the instructions. Output that isn't a verbatim quote is rejected anyway.

### Audit record

`pruefprotokoll.json` holds the tenant, the SHA-256 of the input document, the lb-lint version, start and end times, and the offset repairs and rejections, with rejected quotes verbatim. For every LLM call it also holds the model, a SHA-256 of the full request (including the output schema), the effort setting, token counts and cost in EUR.

## LLM provider and data residency

The target provider is **Mistral (EU-hosted)**, because public-sector documents come with data-residency expectations ([D-001](DECISIONS.md)). **The current build runs on Anthropic (`claude-haiku-5-5`)** as an interim development provider ([D-010](DECISIONS.md)). All LLM calls go through one module ([`providers.py`](src/lb_lint/providers.py)), and `LB_LINT_MODELL` selects the model. Until Mistral is wired in, EU data residency is designed, not running. **Do not process real procurement documents with this build.**

## Known limitations

The main ones: above-threshold (VgV) procurement only, brand references only (not origin or process), a noisy LB202, and no quality measurement yet. The full list, with the reasoning behind each item, is in **[LIMITATIONS.md](LIMITATIONS.md)**.

## Project records

The project keeps its reasoning in the open:

- [DECISIONS.md](DECISIONS.md): architecture decisions, with the alternatives rejected and why.
- [INCIDENTS.md](INCIDENTS.md): what went wrong, what it was first thought to be, and what it actually was.
- [METRICS.md](METRICS.md): dated measurements, early numbers kept.
- [PLAN.md](PLAN.md): the full build plan (M1–M6) and non-goals.
- [notes/reading.md](notes/reading.md): the statute text these rules are built on.

## Roadmap

| Milestone | Status |
|---|---|
| M1 — Vertical slice: draft in, audited findings out | done |
| M2 — Eval harness on a hand-annotated golden set, CI quality gate | next |
| M3 — Corpus of real TED notices, hybrid retrieval, CPV clustering | planned |
| M4 — LangGraph orchestration with critique loop and budget guard | planned |
| M5 — Async backend (RabbitMQ, socket.io), review UI | planned |
| M6 — Knowledge graph, full provenance | planned |
