"""All deterministic rule checks (D-003). Verdicts never depend on an LLM call."""

from lb_lint.models import Anforderung, Befund
from lb_lint.rules import eindeutigkeit, produktneutral
from lb_lint.rules.saetze import fenster


def pruefe(quelle: str, anforderungen: list[Anforderung]) -> list[Befund]:
    """Run every rule on the source; attach each finding to the Anforderung containing it."""
    befunde = produktneutral.pruefe(quelle, fenster(quelle)) + eindeutigkeit.pruefe_vage(quelle)
    for b in befunde:
        b.anforderung_id = next(
            (a.id for a in anforderungen if a.span.start <= b.span.start and b.span.end <= a.span.end), None
        )
    befunde += eindeutigkeit.pruefe_messbarkeit(anforderungen)
    return sorted(befunde, key=lambda b: (b.span.start, b.regel_id))
