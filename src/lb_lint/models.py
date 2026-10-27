"""Core data models: requirements, findings, and the audit record."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, computed_field, model_validator


class Kategorie(StrEnum):
    TECHNISCH = "technisch"
    DIENSTLEISTUNG = "dienstleistung"
    LIEFERUNG = "lieferung"
    SONSTIGE = "sonstige"


class Schwere(StrEnum):
    FEHLER = "fehler"
    WARNUNG = "warnung"
    HINWEIS = "hinweis"


class Span(BaseModel):
    """Half-open character range [start, end) into the source document."""

    start: int = Field(ge=0)
    end: int

    @model_validator(mode="after")
    def _ordered(self) -> "Span":
        if self.end <= self.start:
            raise ValueError(f"empty or inverted span: {self.start}..{self.end}")
        return self


class Abschnitt(BaseModel):
    """A section of the document, delimited by Markdown headings; the LLM's unit of work (D-009)."""

    nummer: int = Field(ge=0, description="0 = preamble before the first section heading, then 1, 2, …")
    titel: str
    span: Span


class AnforderungEntwurf(BaseModel):
    """What the LLM returns. No offsets or IDs: code locates `text` in the source (D-008)."""

    text: str = Field(description="Wörtliches Zitat der Anforderung aus dem Abschnitt, unverändert")
    kategorie: Kategorie
    messbar: bool = Field(description="Enthält die Anforderung einen prüfbaren Wert mit Einheit?")


class Anforderung(BaseModel):
    """One extracted requirement. `id` is for storage, `label` for people (D-005)."""

    id: str = Field(pattern=r"^[0-9a-f]{12}(-\d+)?$")
    label: str = Field(pattern=r"^A-\d+-\d+$")
    text: str
    span: Span
    abschnitt: int = Field(ge=0)
    kategorie: Kategorie
    messbar: bool


class Befund(BaseModel):
    """One finding: a proposal for a human to accept or reject (T3)."""

    regel_id: str = Field(pattern=r"^LB\d{3}$")
    regel_name: str
    schwere: Schwere
    anforderung_id: str | None = Field(description="Containing Anforderung, if any (D-011)")
    begruendung: str
    rechtsgrundlage: str
    span: Span
    zitat: str = Field(description="Must equal source[span.start:span.end]")


class LlmAufruf(BaseModel):
    """One LLM call crossing the data-residency boundary (T2)."""

    model_id: str
    prompt_sha256: str
    temperature: float | None = Field(default=None, description="Only if the provider accepted it (I-002)")
    effort: str | None = Field(default=None, description="None = provider default")
    thinking: str | None = Field(default=None, description="None = provider default")
    seed: int | None = None
    input_tokens: int
    output_tokens: int
    cost_eur: Decimal
    timestamp: datetime


class Pruefprotokoll(BaseModel):
    """Audit record for one run: enough to reproduce every finding."""

    tenant_id: str
    dokument_sha256: str
    lb_lint_version: str
    gestartet: datetime
    beendet: datetime
    aufrufe: list[LlmAufruf]
    offset_repariert: int = Field(ge=0, description="Quotes located only by whitespace-tolerant matching")
    offset_verworfen: int = Field(ge=0, description="Quotes not located in the source at all")
    verworfene_zitate: list[str] = Field(default_factory=list, description="The rejected quotes, verbatim")
    abbruch_grund: str | None = None

    @computed_field
    @property
    def input_tokens(self) -> int:
        return sum(a.input_tokens for a in self.aufrufe)

    @computed_field
    @property
    def output_tokens(self) -> int:
        return sum(a.output_tokens for a in self.aufrufe)

    @computed_field
    @property
    def cost_eur(self) -> Decimal:
        return sum((a.cost_eur for a in self.aufrufe), Decimal(0))
