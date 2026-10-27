"""The M1 linear pipeline: segment → extract → rules, with the audit record."""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version

from pydantic_ai.models import Model

from lb_lint import rules
from lb_lint.extract import extrahiere
from lb_lint.models import Anforderung, Befund, Pruefprotokoll
from lb_lint.segment import abschnitte


@dataclass
class Pruefung:
    anforderungen: list[Anforderung]
    befunde: list[Befund]
    protokoll: Pruefprotokoll


def pruefe_dokument(quelle: str, tenant_id: str = "default", modell: str | Model | None = None) -> Pruefung:
    gestartet = datetime.now(UTC)
    extraktion = extrahiere(quelle, abschnitte(quelle), modell=modell)
    befunde = rules.pruefe(quelle, extraktion.anforderungen)
    protokoll = Pruefprotokoll(
        tenant_id=tenant_id,
        dokument_sha256=hashlib.sha256(quelle.encode()).hexdigest(),
        lb_lint_version=version("lb-lint"),
        gestartet=gestartet,
        beendet=datetime.now(UTC),
        aufrufe=extraktion.aufrufe,
        offset_repariert=extraktion.repariert,
        offset_verworfen=len(extraktion.verworfen),
        verworfene_zitate=extraktion.verworfen,
    )
    return Pruefung(extraktion.anforderungen, befunde, protokoll)
