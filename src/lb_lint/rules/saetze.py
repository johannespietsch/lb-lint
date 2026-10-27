"""Deterministic sentence windows for the rule checks (D-011, I-001).

No statistical model: the same text always gives the same windows. Hard boundaries
are blank lines, headings and list items; inside a block, a sentence ends at
`.`, `!` or `?` followed by whitespace, unless the full stop belongs to an
abbreviation or follows a number (German ordinals: "der 13. Generation").
Statute names (VgV, GWB, UVgO) carry no full stop of their own, so a full stop
after them always ends the sentence.
"""

import re

from lb_lint.models import Span

ABKUERZUNGEN = frozenset(
    "abs nr ggf inkl bzw ca gem evtl max min mind usw vgl ziff lit buchst zzgl ggü bspw tel str art anl insb sog".split()
)

BLOCKGRENZE = re.compile(r"\n[ \t]*\n|\n(?=[ \t]*(?:#{1,6}[ \t]|[-*+][ \t]|\d+\.[ \t]))")
SATZENDE = re.compile(r"[.!?](?=\s)")


def fenster(quelle: str) -> list[Span]:
    """All sentence windows of `quelle`, stripped of surrounding whitespace and list markers."""
    spans = []
    start = 0
    for m in BLOCKGRENZE.finditer(quelle):
        spans += _saetze(quelle, start, m.start())
        start = m.end()
    spans += _saetze(quelle, start, len(quelle))
    return spans


def _saetze(quelle: str, start: int, ende: int) -> list[Span]:
    spans = []
    satzanfang = start
    for m in SATZENDE.finditer(quelle, start, ende):
        wort = re.search(r"(\S+)$", quelle[satzanfang : m.start()])
        if wort and _kein_satzende(wort.group(1)):
            continue
        spans.append((satzanfang, m.end()))
        satzanfang = m.end()
    spans.append((satzanfang, ende))
    return [s for a, e in spans if (s := _bereinigt(quelle, a, e))]


def _kein_satzende(wort: str) -> bool:
    wort = wort.lstrip("(")
    return wort.isdigit() or len(wort) == 1 or wort.lower() in ABKUERZUNGEN


def _bereinigt(quelle: str, start: int, ende: int) -> Span | None:
    text = quelle[start:ende]
    kopf = re.match(r"\s*(?:#{1,6}[ \t]+|[-*+][ \t]+)?", text).end()
    rest = text[kopf:].rstrip()
    if not rest:
        return None
    return Span(start=start + kopf, end=start + kopf + len(rest))
