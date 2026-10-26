"""Split a Markdown Leistungsbeschreibung into Abschnitte by heading (D-009)."""

import re
from collections import Counter

from lb_lint.models import Abschnitt, Span

UEBERSCHRIFT = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$", re.MULTILINE)


def abschnitte(quelle: str) -> list[Abschnitt]:
    """Sections start at the most frequent heading level (ties: the higher level).

    Text before the first such heading is the preamble, section 0, if it is not
    blank. Lower-level headings stay inside their parent section. Spans are
    contiguous and cover the whole document from the first kept section on.
    """
    treffer = list(UEBERSCHRIFT.finditer(quelle))
    if not treffer:
        return [_praeambel(len(quelle))] if quelle.strip() else []

    ebenen = Counter(len(m.group(1)) for m in treffer)
    ebene = max(ebenen, key=lambda e: (ebenen[e], -e))
    starts = [m for m in treffer if len(m.group(1)) == ebene]

    ergebnis = []
    if quelle[: starts[0].start()].strip():
        ergebnis.append(_praeambel(starts[0].start()))
    for i, m in enumerate(starts):
        ende = starts[i + 1].start() if i + 1 < len(starts) else len(quelle)
        ergebnis.append(Abschnitt(nummer=i + 1, titel=m.group(2), span=Span(start=m.start(), end=ende)))
    return ergebnis


def _praeambel(ende: int) -> Abschnitt:
    return Abschnitt(nummer=0, titel="Präambel", span=Span(start=0, end=ende))
