"""Locate LLM quotes in the source and compute their offsets (D-008)."""

import re
from dataclasses import dataclass
from enum import StrEnum

from lb_lint.models import Span


class Treffer(StrEnum):
    EXAKT = "exakt"
    REPARIERT = "repariert"


@dataclass(frozen=True)
class Fundstelle:
    span: Span
    treffer: Treffer


def lokalisiere(zitat: str, quelle: str, offset: int, belegt: set[int]) -> Fundstelle | None:
    """Find `zitat` in `quelle` (a section starting at absolute `offset`).

    Exact match first, then whitespace-tolerant. Occurrences whose absolute start
    is in `belegt` are skipped, so duplicates are assigned in order; the caller
    adds the returned start to `belegt`. Returns None if the quote is not found.
    """
    zitat = zitat.strip()
    if not zitat:
        return None

    pos = quelle.find(zitat)
    while pos != -1:
        if offset + pos not in belegt:
            return Fundstelle(Span(start=offset + pos, end=offset + pos + len(zitat)), Treffer.EXAKT)
        pos = quelle.find(zitat, pos + 1)

    muster = re.compile(r"\s+".join(re.escape(t) for t in zitat.split()))
    for m in muster.finditer(quelle):
        if offset + m.start() not in belegt:
            return Fundstelle(Span(start=offset + m.start(), end=offset + m.end()), Treffer.REPARIERT)
    return None
