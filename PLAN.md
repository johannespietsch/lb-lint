# lb-lint — Plan

### Ein Linter für Leistungsbeschreibungen.

*An agentic checking pipeline that breaks a draft Leistungsbeschreibung (tender specification) into structured, individually traceable requirements, checks them for product neutrality and unambiguity, surfaces comparable requirements from published tender notices — and produces an audit-proof provenance record for every statement it makes. With an eval gate: no prompt change gets through CI if it lowers the hit rate on the golden set.*

Think `ruff`, but for German tender specifications. Every finding has a rule ID, a character span in the source document, a legal basis, and a reproducible provenance record.

> **lb-lint is a linter, not legal advice.** It flags patterns against two named provisions of German procurement law. Every finding is a proposal for a human to accept or reject. It does not replace review by a procurement lawyer.

---

## 1. The problem

Anyone who writes public tender documents with the help of generative AI runs into the same contradiction: procurement documents have to be **revisionssicher** — traceable, reproducible, defensible — and a language model is none of those things by default. If a Leistungsbeschreibung is challenged in a review procedure (Nachprüfungsverfahren), the contracting authority will be asked: *which sentence came from where, on what basis, and can you reproduce it?* "The model wrote it" is not an answer that survives a Vergabekammer.

Two formal defects come up constantly in drafts, and both are machine-checkable:

- **Produktneutralität.** § 31 Abs. 6 VgV forbids a Leistungsbeschreibung from referring to a specific make, origin, or process that favours particular undertakings — unless justified *and* accompanied by *"oder gleichwertig."* Drafts written by people who know exactly which laptop they want violate this all the time. It is one of the most common formal defects, and getting it wrong can void a procurement.
- **So eindeutig wie möglich.** § 121 Abs. 1 GWB requires the Leistungsbeschreibung to describe the subject matter as unambiguously as possible, so that all bidders understand it the same way (below the thresholds, § 23 Abs. 1 UVgO adds *"erschöpfend"*). "Ausreichende Performance" is not a requirement; it is a future dispute.

`lb-lint` is the quality gate that sits between whatever *produced* a Leistungsbeschreibung — a person, a template, or an LLM — and the human who *signs* it. It is designed for contracting authorities, procurement consultancies, and vendors of tender-drafting software who need machine-assisted drafting without giving up traceability.

---

## 2. Architecture

### Trust boundaries

These are the core of the design.

- **T1 — Untrusted input.** The draft document. Never interpolated into a system prompt unescaped; it is a prompt-injection surface (a supplier's market-consultation response pasted into a draft could contain "ignore previous instructions").
- **T2 — Data-residency boundary.** Everything sent to an LLM provider crosses this. The primary provider is EU-hosted (Mistral). The boundary is a single chokepoint module, so swapping providers is a config change and the question "where does our data go?" has one concrete answer.
- **T3 — Advisory boundary.** The agent *flags*; it never *decides*. Every finding is a proposal with a confidence and a legal reference, for a human to accept or reject. That is the design that is safe under the EU AI Act, and the honest one.
- **T4 — Tenant boundary.** Every audit record carries `tenant_id`; retrieval is tenant-scoped. Stubbed, but designed in from the start, because bolting multi-tenancy on later is what kills products like this.

```mermaid
flowchart TB
    subgraph client["Browser (T1: untrusted input)"]
        UI["Minimal review UI<br/>findings + accept/reject"]
    end

    subgraph api["FastAPI"]
        REST["POST /pruefung<br/>GET /pruefung/:id"]
        SIO["socket.io<br/>progress + partial findings"]
    end

    MQ[["RabbitMQ<br/>pruefung.jobs"]]

    subgraph worker["Worker process"]
        subgraph graph["LangGraph state machine"]
            SEG["segment<br/>spaCy de_core_news_lg"]
            EXT["extract_anforderungen<br/>PydanticAI, typed + offsets"]
            RULE["rule_checks<br/>§31(6) VgV, §121 GWB<br/>deterministic"]
            RET["retrieve_vergleichbare<br/>hybrid: pgvector + german tsvector"]
            CRIT["critique<br/>LLM-as-judge, budgeted"]
            REV["revise<br/>max 2 loops"]
            BUD{{"budget guard<br/>tokens / EUR / loops"}}
        end
    end

    subgraph llm["T2: data-residency boundary"]
        MISTRAL["Mistral (EU-hosted) — primary"]
        ANTHROPIC["Anthropic — eval comparison only"]
    end

    subgraph store["Postgres 16 + pgvector (SQLAlchemy 2.0)"]
        DOCS[("dokumente / abschnitte")]
        FIND[("befunde — findings<br/>+ char offsets")]
        AUDIT[("pruefprotokoll<br/>prompt_hash, model_id,<br/>seed, cost, tenant_id")]
        CORP[("bekanntmachungen<br/>TED corpus + embeddings")]
        KG[("anforderung → CPV → norm<br/>edges")]
    end

    subgraph eval["Eval harness"]
        GOLD["golden_set/ — 25 hand-annotated<br/>German excerpts"]
        SCORE["pytest -m eval<br/>F1 + determinism + cost"]
        GATE{{"CI gate: F1 ≥ 0.75<br/>determinism ≥ 0.95"}}
    end

    UI -->|"upload draft"| REST
    REST -->|"enqueue"| MQ
    MQ --> graph
    SEG --> EXT --> RULE --> RET --> CRIT
    CRIT -->|"findings weak"| REV
    REV --> RULE
    CRIT -->|"ok"| FIND
    BUD -.->|"halt"| FIND
    EXT <--> MISTRAL
    CRIT <--> MISTRAL
    RET --> CORP
    RULE --> KG
    graph -->|"per-node events"| SIO
    SIO --> UI
    graph --> AUDIT
    graph --> DOCS
    GOLD --> SCORE --> GATE
    SCORE -.->|"replays"| graph
    ANTHROPIC -.-> SCORE
```

### Components

| Component | What it does | Why it is built this way |
|---|---|---|
| **`segment/`** | spaCy `de_core_news_lg` pipeline with custom abbreviation rules for `Abs.`, `Nr.`, `ggf.`, `z. B.`, `i. V. m.` | German administrative text is not English text with umlauts; legal citations break off-the-shelf sentence segmentation |
| **`extract/`** | PydanticAI agent returning `list[Anforderung]` with mandatory `(start, end)` character offsets, validated against the source | Typed LLM output with structural validation; offsets are what make findings clickable and auditable |
| **`rules/`** | Deterministic checks: brand-name gazetteer + `oder gleichwertig` proximity (§ 31 Abs. 6 VgV), vagueness lexicon (§ 121 Abs. 1 GWB), missing-unit detection | Legally load-bearing checks live *outside* the model. This is how an LLM product can be revisionssicher |
| **`retrieve/`** | Hybrid search over ~200 real German TED notices: `pgvector` cosine + Postgres `to_tsvector('german', …)` full-text ranking, reciprocal-rank fusion | Hybrid retrieval with German text-search config; Postgres FTS instead of a separate search cluster |
| **`cluster/`** | scikit-learn `KMeans` over notice embeddings, `k` chosen by silhouette; cluster → dominant CPV code → suggested requirement template | Unsupervised structure discovery with a defensible `k`, not a magic number |
| **`graph/`** | `networkx` graph `Anforderung → CPV → Rechtsnorm → Befund`, queried for "which norms does this section touch" | A knowledge graph that does actual retrieval work, not a diagram |
| **`orchestrate/`** | LangGraph `StateGraph`: segment → extract → rules → retrieve → critique → (revise ≤ 2) → persist, with a budget-guard node | Explicit agentic workflow with hard termination conditions and per-node cost accounting |
| **`api/`** | FastAPI + `python-socketio` (`AsyncAioPikaManager`), job submit/poll, per-node progress events | Checking a long document takes minutes, not milliseconds; the user watches progress instead of a spinner |
| **`worker/`** | RabbitMQ consumer that runs the graph | Long-running LLM jobs decoupled from the request cycle; jobs survive API restarts |
| **`db/`** | SQLAlchemy 2.0 declarative models + Alembic migrations, `tenant_id` on every row, `pruefprotokoll` audit table | Auditability and multi-tenancy as schema requirements, not afterthoughts |
| **`eval/`** | 25 hand-annotated German excerpts; span-F1 for extraction, P/R for the § 31(6) flag, determinism rate over 5 runs, EUR per document; `pytest -m eval`; CI fails below threshold | **The centrepiece.** Quality is a number, and regressions block merges |
| **`tests/`** | Unit (rules, offsets), integration (graph against a stubbed LLM), E2E (upload → socket events → findings, via `httpx` + testcontainers) | The full test pyramid; CI runs without an API key |
| **`providers/`** | Single LLM chokepoint; Mistral (EU) by default, Anthropic behind a flag for eval comparison only; every call logged with token count and EUR | Data residency enforced in one place; the quality cost of the EU choice is measured, not assumed |
| **`web/`** | One HTML page, htmx, no framework | Human-in-the-loop accept/reject for the person who signs the document |
| **`DECISIONS.md` / `INCIDENTS.md` / `METRICS.md`** | Architecture decision log, incident log, dated metrics | See section 5 |

---

## 3. Non-goals

These keep the project scoped. Violating any of them is how it doubles in size.

1. **No document parsing.** Input is `.txt` / `.md` only. PDF/DOCX extraction is a hard, separate problem. A converter script that shells out to `pandoc` is the most this project does.
2. **No generation of Leistungsbeschreibungen.** `lb-lint` only *checks*. It is a complement to drafting tools, not a competitor.
3. **No authentication, no user management, no real multi-tenancy.** `tenant_id` is in the schema and threaded through queries. There is no login. Designed for it, not built.
4. **No frontend framework.** One server-rendered HTML page with htmx.
5. **No cloud deployment.** `docker compose up` locally.
6. **No finetuning, no model training.** Build the eval first; whether finetuning is ever the right answer is a question the eval answers.
7. **No legal correctness claim.** `lb-lint` flags patterns against two named provisions. The disclaimer goes in the README's first paragraph.
8. **No more than 200 corpus documents.** Enough for meaningful retrieval and clustering; small enough to embed in minutes.

---

## 4. Build plan

Six milestones, ~16 hours total. Milestone 1 alone is demoable; M1 + M2 is the minimum meaningful release.

| Milestone | Hours | Running |
|---|---|---|
| M1 — Vertical slice | 4.0 | 4.0 |
| M2 — Eval harness + CI gate | 3.0 | 7.0 |
| M3 — Corpus, hybrid retrieval, clustering | 3.0 | 10.0 |
| M4 — LangGraph + budget guard | 3.0 | 13.0 |
| M5 — RabbitMQ + socket.io + E2E | 2.0 | 15.0 |
| M6 — Knowledge graph, audit trail, README | 1.0 | 16.0 |

### Before M1 — domain reading

Reading makes the sample document and the rules credible instead of plausible:

1. **§ 31 VgV** and **§ 121 GWB** on `gesetze-im-internet.de` — the exact wording of the product-neutrality exception and the *"oder gleichwertig"* requirement. This is the legal basis of the entire rule engine.
2. **UVgO §§ 22–23** — how the below-threshold regime differs. Most municipal procurement happens below EU thresholds, under UVgO rather than VgV.
3. **eForms / the German Bekanntmachungsservice** (`oeffentlichevergabe.de`) — what a structured notice contains and what CPV codes are for.

---

### M1 — Vertical slice: draft in, audited findings out (4.0h)

**Goal:** A single command turns a German draft Leistungsbeschreibung into a JSON list of extracted requirements, each with a § 31(6) VgV verdict, character offsets into the source, and a reproducible audit record.

**Done when:** `make demo` on `samples/laptops_schulen.md` prints ≥ 8 extracted `Anforderung` objects; at least one is flagged `PRODUKTNEUTRALITAET_VERLETZT` with the offending brand span; every finding's `(start, end)` slice of the source equals its quoted text; and `pruefprotokoll.json` contains `model_id`, `prompt_sha256`, `temperature`, `input_tokens`, `output_tokens`, `cost_eur`, `timestamp`.

**Steps:**

1. `uv init`, Python 3.12. `uv add pydantic-ai spacy python-dotenv rich typer`, then `uv run python -m spacy download de_core_news_lg`.
2. **Create `DECISIONS.md`, `INCIDENTS.md`, `METRICS.md` before any code** (templates in section 5). Seed the first three decisions (D-001 to D-003, below).
3. Write `samples/laptops_schulen.md` by hand — ~2 pages of plausible German Leistungsbeschreibung for a school laptop procurement. **Include deliberate defects:** a named brand without *"oder gleichwertig"*, a vague requirement (*"ausreichende Akkulaufzeit"*), a requirement with no measurable unit, and several correct requirements. This file is also the first eval fixture.
4. `src/lb_lint/models.py`: Pydantic models. `Anforderung(id, text, start, end, abschnitt, kategorie, messbar: bool)`, `Befund(regel_id, schwere, anforderung_id, begruendung, rechtsgrundlage, span)`, `Pruefprotokoll(...)`.
5. `src/lb_lint/segment.py`: load `de_core_news_lg`, add custom tokenizer/sentencizer rules for German legal abbreviations. Segment into *Abschnitte* by Markdown heading, not by sentence — sections are the LLM's unit of work.
6. `src/lb_lint/extract.py`: PydanticAI `Agent` with `output_type=list[AnforderungEntwurf]`. Prompt in German. Pass one Abschnitt; the model returns verbatim quotes only, and code locates each quote in the source and computes the offsets (D-008). Quotes that cannot be located are rejected and counted.
7. `src/lb_lint/rules/produktneutral.py`: gazetteer of ~40 IT brand names (`Dell`, `Lenovo`, `ThinkPad`, `Microsoft Office`, `Windows 11`, `Intel Core i7`, …) + spaCy `PhraseMatcher`. Flag a match unless *"oder gleichwertig"* / *"oder vergleichbar"* appears in the same sentence. `rechtsgrundlage="§ 31 Abs. 6 VgV"`.
8. `src/lb_lint/rules/eindeutigkeit.py`: vagueness lexicon (`ausreichend`, `angemessen`, `zeitnah`, `nach Bedarf`, `marktüblich`, `hochwertig`) → `rechtsgrundlage="§ 121 Abs. 1 GWB"`.
9. `src/lb_lint/providers.py`: one function; all LLM calls go through it. Returns `(result, usage)`. Logs tokens and EUR. Mistral via `pydantic_ai.models.mistral`.
10. `src/lb_lint/cli.py` (typer): `lb-lint pruefe <file> --json`. `Makefile` targets `demo`, `test`, `eval`, `up`, `fmt`.
11. Record the first `METRICS.md` numbers: extraction count, wall time, cost in EUR, tokens. **Keep the bad first number** — it is the baseline everything else is measured against.

**Trap:** spaCy's German sentencizer splits *"gemäß § 31 Abs. 6 VgV"* after `Abs.` and *"z. B. Notebooks"* after `B.`, shredding requirements mid-sentence and producing offsets that point at fragments. Symptom: flagged spans look truncated. Two fixes, and the second is the real one: add abbreviation exceptions to the tokenizer — *and then stop sentence-segmenting before extraction altogether.* Segment by heading, let the LLM see whole sections, and use sentences only inside the deterministic rule checks, where a bounded window is actually needed. Log both the wrong fix and the right one in `INCIDENTS.md`.

**Second trap:** the model returns requirement text that is *paraphrased* rather than verbatim — subtly, perhaps 20% of the time: normalised whitespace, an expanded abbreviation. Offsets then point at almost-but-not-quite the right span, which nobody notices until a finding highlights the wrong sentence in the UI. The offset validator in step 6 catches it. Log the rejection rate; it is a real metric of model reliability.

**Fallback:** drop the section splitter; run extraction on the whole document in one call and implement one rule (Produktneutralität only). Still a demo, an audit record, and verified offsets.

---

### M2 — Eval harness and the CI gate (3.0h)

**Goal:** Any change to a prompt, model, or rule produces a measured, comparable quality number, and CI refuses a regression.

**Done when:** `make eval` prints a table with span-level extraction F1, § 31(6) precision/recall, determinism rate over 5 runs at temperature 0, mean EUR per document, and p95 latency; `pytest -m eval` exits non-zero when extraction F1 < 0.75 or determinism < 0.95; and `eval/runs/` holds at least two dated runs that can be diffed.

**Steps:**

1. **Write `eval/ANNOTATION_GUIDELINES.md` before annotating anything.** The hard question is *"is a bullet with three sub-clauses one Anforderung or three?"* Decide, write it down, follow it.
2. Build `eval/golden_set/` — 25 German excerpts (the `samples/` file split up, plus ~15 excerpts from real German TED notices; fetch those now, M3 needs them anyway). Annotate **from the raw text, before running the model on it.**
3. `eval/score.py`: span-level F1 with IoU ≥ 0.5 as a match for extraction; exact set comparison P/R for the Produktneutralität flag.
4. Determinism harness: run the same document 5× at `temperature=0`, hash the normalised finding set, report the fraction of identical runs. **Expect this to be below 1.0.** That is a finding, not a bug in the harness.
5. `tests/test_rules.py` (unit, no LLM — the gazetteer and lexicon must be fast and deterministic), `tests/test_extract_contract.py` (integration against a recorded/stubbed LLM response, so CI runs without an API key).
6. `.github/workflows/eval.yml`: unit + integration on every push; `-m eval` nightly or on `[eval]` in the commit message. Record the reason for the split (cost) in `DECISIONS.md`.
7. `METRICS.md`: dated baseline table. Then change one thing — the prompt, or `mistral-small` → `mistral-large` — and record the delta.

**Trap:** label leakage. It is tempting to run the extractor first and annotate by correcting its output. Do that and F1 will be ~0.95 and mean nothing — it measures the model's agreement with itself. Annotate blind. The flip side: your own annotations will be internally inconsistent (compound requirements split differently on Monday than on Tuesday), and the guidelines from step 1 are the only defence. Re-annotate excerpts 1–5 at the end and measure self-agreement. If it is below ~0.85, the guidelines are too loose — tighten them and record that.

**Fallback:** 12 excerpts instead of 25; extraction F1 and determinism only. A gate on two metrics still gates.

---

### M3 — Real corpus, hybrid retrieval, clustering (3.0h)

**Goal:** For any extracted requirement, the system surfaces comparable requirements from real published German tender notices and suggests a CPV code.

**Done when:** Postgres holds ≥ 150 German notices with embeddings; `lb-lint aehnlich "<requirement text>"` returns 5 ranked comparable passages with source notice IDs; hybrid (vector + German FTS) measurably beats vector-only on a 15-query set; and `lb-lint cluster` prints k clusters with their silhouette score and dominant CPV code.

**Steps:**

1. `docker-compose.yml`: `pgvector/pgvector:pg16`. `uv add sqlalchemy alembic psycopg[binary] pgvector sentence-transformers scikit-learn`.
2. **Fetch the corpus.** TED (Tenders Electronic Daily) publishes EU tender notices as open, reusable data — bulk exports via data.europa.eu and a search API under `api.ted.europa.eu`. Filter to `country=DE`, German-language, IT/equipment CPV divisions (30xxxxxx, 48xxxxxx). **Verify the current endpoint shape and export format before starting — the API is versioned and its docs are the authority.** Implement as `scripts/fetch_corpus.py` with an on-disk cache so the corpus is fetched once.
3. SQLAlchemy 2.0 models + Alembic migration: `bekanntmachung(id, tenant_id, titel, beschreibung, cpv, veroeffentlicht_am, embedding vector(768), tsv tsvector)`. Generated column `to_tsvector('german', titel || ' ' || beschreibung)`. GIN index on `tsv`, HNSW on `embedding`.
4. Embeddings: `intfloat/multilingual-e5-base` (768-dim, strong on German, runs on CPU). Alternatives worth a `DECISIONS.md` entry: `T-Systems-onsite/german-roberta-sentence-transformer-v2`, or Mistral's embedding API — the latter sends corpus data across T2.
5. `retrieve/hybrid.py`: reciprocal-rank fusion of pgvector cosine top-20 and `ts_rank_cd` top-20. Tenant-scoped.
6. Write 15 German queries with known-relevant notices; measure MRR@5 for vector-only, FTS-only, and hybrid. All three numbers go in `METRICS.md`.
7. `cluster/cpv.py`: `KMeans` over notice embeddings, sweep `k` ∈ [4, 20], pick by silhouette, report the dominant CPV per cluster as a sanity check on whether the clusters mean anything.
8. Wire retrieval into the pipeline as an enrichment step on each `Anforderung`.

**Trap:** the `e5` family requires `"query: "` and `"passage: "` prefixes on inputs. Omit them and retrieval still *works* — just quietly worse, with no error anywhere. The MRR measurement in step 6 is the only thing that catches it, which is the whole argument for measuring retrieval before trusting it. **Second trap:** German compounding. *"Ladesäuleninfrastruktur"* and *"Infrastruktur für Ladesäulen"* mean nearly the same thing, and the FTS half scores them as unrelated (the `german` text-search config stems, it does not decompound). Either let the vector half carry those queries or add a decompounding step — but log it in `INCIDENTS.md` either way.

**Fallback:** skip TED; hand-save 40 notices from a public state procurement portal. Skip clustering; do nearest-neighbour CPV suggestion instead.

---

### M4 — LangGraph orchestration with a budget guard (3.0h)

**Goal:** The pipeline becomes an explicit agentic state machine with a critique/revise loop that cannot run away on cost.

**Done when:** `lb-lint pruefe --graph` executes a LangGraph `StateGraph`; the run emits per-node token and EUR accounting; the critique node triggers at most 2 revisions; a document engineered to provoke looping terminates on the budget guard and records `abbruch_grund="budget"` in the audit record; and the M2 eval suite runs against the graph path, showing the F1 delta vs. the M1 linear path.

**Steps:**

1. `uv add langgraph`. `orchestrate/graph.py`: `StateGraph` over a `PruefungState` TypedDict carrying `abschnitte`, `anforderungen`, `befunde`, `kosten_eur`, `tokens`, `revisionen`, `abbruch_grund`.
2. Nodes: `segment` → `extract` → `rule_checks` → `retrieve` → `critique` → conditional edge → `revise` (back to `rule_checks`) or `persist`.
3. `critique`: LLM-as-judge in German, scoring each finding as *begründet / unbegründet / unklar*. Cheap model. Its job is to catch gazetteer false positives (e.g. "Windows" in a *Fenster* context, `Office` in an address).
4. `budget_guard`: checked on every node transition. Hard caps on total EUR, total tokens, and revision count. On trip, short-circuit to `persist` with `abbruch_grund` set. **Partial results are always persisted** — work is never discarded on budget exhaustion.
5. Per-node cost accounting written into `pruefprotokoll`.
6. Re-run `make eval` through the graph. Record F1, cost, and latency deltas in `METRICS.md`. **If the agent is worse, or not better enough per euro, than the linear pipeline, report that.** It is a legitimate result.

**Trap:** cost blowup. A 40-requirement document × critique per requirement × 2 revision rounds is 120+ LLM calls, and if the critique prompt includes the retrieved comparables (tempting — it improves the critique), each call carries several thousand extra tokens. Fix in three layers: batch the critique (all findings for one section in one call); cache by `sha256(prompt + model + params)` so revisions don't re-pay for unchanged sections; cap hard. Record the actual before/after EUR per document in `METRICS.md`.

**Second trap:** determinism gets *worse* with the critique loop, because the judge's borderline calls flip between runs and change the revision path. The M2 determinism gate starts failing. **Do not delete the gate.** This is the central tension of the project — *agents improve quality and erode reproducibility, and the requirement is revisionssicher.* Resolve it explicitly: pin the seed where the provider supports it, make the deterministic rule checks authoritative for anything carrying a `rechtsgrundlage`, and let the agent only ever *add advisory context*, never *remove or override a rule-based finding*. Record that boundary in `DECISIONS.md` as an architectural invariant.

**Fallback:** keep the linear pipeline as the default path; implement the graph with critique but *no* revise edge (single-pass judging). Still a budgeted state machine, one loop fewer.

---

### M5 — Async backend: RabbitMQ worker + socket.io progress (2.0h)

**Goal:** Submitting a document returns immediately; the browser watches the graph execute node by node.

**Done when:** `POST /pruefung` returns a job ID in < 200 ms; a separate worker process consumes from RabbitMQ and runs the graph; the browser receives a `knoten_fertig` socket.io event per graph node with partial findings; and an E2E test drives upload → events → final result against a real broker and a stubbed LLM.

**Steps:**

1. `uv add fastapi uvicorn python-socketio aio-pika httpx pytest-asyncio`. Add `rabbitmq:3-management` to compose.
2. `api/main.py`: `POST /pruefung` (persist + publish to `pruefung.jobs`, return `job_id`), `GET /pruefung/{id}`.
3. `worker/main.py`: `aio_pika` consumer; runs the LangGraph; emits progress.
4. Mount `socketio.ASGIApp` on the FastAPI app. Clients join room `job_{id}`.
5. **Emit from the worker** via `socketio.AsyncAioPikaManager` (or `AsyncRedisManager`) so events cross the process boundary.
6. `web/index.html`: htmx + the socket.io client. A list of findings that fills in live, each with an accept/reject button that `POST`s a `bewertung`. That accept/reject log is the human-in-the-loop record — and future eval data.
7. `tests/test_e2e.py`: `httpx.AsyncClient` + a socket.io test client, real Postgres and RabbitMQ via compose, LLM stubbed. Marked `-m e2e`.

**Trap:** progress events emitted from the worker never reach the browser — silently, with no error on either side. The FastAPI process and the worker each have their own in-memory socket.io server and don't know about each other; the worker emits into a void. The client manager in step 5 is the fix. **Second trap:** a worker that crashes mid-graph leaves the job in `laufend` forever and the browser spinning. Add a job timeout and a terminal `fehlgeschlagen` state with partial findings attached — never a spinner with no exit.

**Fallback:** drop RabbitMQ; use FastAPI `BackgroundTasks` + in-process socket.io (single process, no cross-process manager). Loses durable job handling — take it only if out of time.

---

### M6 — Knowledge graph, audit trail, and the README (1.0h)

**Goal:** Findings are connected to legal norms in a queryable graph, and a stranger can run the whole thing.

**Done when:** `lb-lint graph --abschnitt 3` prints the norms and CPV codes that section touches, traversed from a `networkx` graph; `pruefprotokoll` for any job reproduces the full provenance of every finding; and `make up && make demo` works from a fresh clone with only `MISTRAL_API_KEY` set.

**Steps:**

1. `graph/build.py`: `networkx.DiGraph`. Nodes: `Anforderung`, `CPV`, `Rechtsnorm`, `Befund`, `Bekanntmachung`. Edges: `verstoesst_gegen`, `belegt_durch`, `aehnlich_zu`, `klassifiziert_als`.
2. Two queries that do real work: *"which norms does section N touch"* and *"which other requirements in the corpus were flagged under the same norm."* The second is the one that actually helps the person reviewing a draft.
3. `README.md`: the problem in procurement vocabulary, the architecture diagram, the quickstart, the current metrics table, the **disclaimer that this is a linter and not legal advice**, and the non-goals from section 3.
4. Final `METRICS.md` pass: baseline vs. current, every number dated.
5. Closing `DECISIONS.md` entry: what would be done differently with a second week.

**Trap:** Neo4j. The Docker image is over a gigabyte, first-run auth has a password-change dance, and the async driver is its own afternoon. `networkx` demonstrates the *modelling*; Neo4j only adds the *install*. Optionally add `graph/cypher_notes.md` with the Cypher equivalents of the two queries.

**Fallback:** skip the graph module; spend the hour on the README and metrics. A project a stranger can't run is worth nothing regardless of what's inside it, so the README is the non-negotiable half of this milestone.

---

## 5. Engineering records

`DECISIONS.md`, `INCIDENTS.md`, and `METRICS.md` are M1 deliverables, created before the first line of pipeline code. They are written as the work happens; they cannot be reconstructed afterwards.

### `DECISIONS.md`

```markdown
## D-00N — <the decision, in one line>
**Datum:** YYYY-MM-DD  **Status:** entschieden | revidiert durch D-00M

**Kontext:** what forced a choice here at all.
**Entscheidung:** what was done.
**Verworfene Alternative(n):** what was not done, and the concrete cost
that ruled it out — not "seemed worse."
**Konsequenz:** what this now makes easy, and what it makes expensive later.
```

Seed entries, written in M1 before coding:

- **D-001 — Mistral (EU-hosted) as primary provider.** Alternative: Anthropic/OpenAI for raw capability. Rejected because public-sector documents come with data-residency expectations, so provider choice is a compliance decision before it is a quality one. Anthropic stays behind a flag as an eval-only comparison, so the quality cost of the choice is *measured rather than assumed*.
- **D-002 — Character offsets mandatory on every extracted requirement.** Alternative: return requirement text only. Rejected because without offsets no finding is verifiable against the source, and *revisionssicher* becomes a claim rather than a property. Cost: a more complex prompt and a validate-and-repair step.
- **D-003 — Legally load-bearing checks are deterministic code, not LLM judgements.** Alternative: ask the model "ist diese Anforderung produktneutral?" Rejected because anything carrying a `rechtsgrundlage` must give the same answer twice, and a model does not. The LLM's role is *extraction and context*; the rules' role is *verdict*.

### `INCIDENTS.md`

```markdown
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
```

Incidents expected along the way: German abbreviation sentence-splitting (M1), paraphrased-span offset drift (M1), golden-set label leakage or self-disagreement (M2), missing `e5` prefixes (M3), German compound decompounding in FTS (M3), agent cost blowup (M4), determinism regression from the critique loop (M4), cross-process socket.io silence (M5).

### `METRICS.md`

Measure from hour one and **keep the early numbers** — a metrics file that starts at 0.91 shows nothing happened.

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

Every row dated. Every change to a prompt or model gets a new dated row.

---

## 6. Stack

Python 3.12 · uv · LangGraph · PydanticAI · spaCy (`de_core_news_lg`) · sentence-transformers (`multilingual-e5-base`) · scikit-learn · networkx · FastAPI · python-socketio · RabbitMQ (aio-pika) · Postgres 16 + pgvector · SQLAlchemy 2.0 + Alembic · htmx · Mistral · pytest + testcontainers · GitHub Actions
