"""§ 121 Abs. 1 GWB: "so eindeutig wie möglich" (D-012).

LB201: vague wording from a fixed lexicon, anywhere in the document.
LB202: an Anforderung with no number and no norm reference — nothing to check an
offer against. Deterministic; the LLM's `messbar` field is advisory only.
"""

import re

from lb_lint.models import Anforderung, Befund, Schwere, Span

RECHTSGRUNDLAGE = "§ 121 Abs. 1 GWB"

VAGE = re.compile(
    r"\b(?:ausreichend|angemessen|zeitnah|marktüblich|hochwertig)\w*|\bnach\s+Bedarf\b",
    re.IGNORECASE,
)
MESSBAR = re.compile(r"\d|\b(?:DIN|EN|ISO|IEC|IEEE|VDE|ETSI)\b")


def pruefe_vage(quelle: str) -> list[Befund]:
    return [
        Befund(
            regel_id="LB201",
            regel_name="vage-formulierung",
            schwere=Schwere.WARNUNG,
            anforderung_id=None,
            begruendung=f"„{m.group()}“ ist nicht für alle Bieter im gleichen Sinne verständlich; durch einen prüfbaren Wert ersetzen.",
            rechtsgrundlage=RECHTSGRUNDLAGE,
            span=Span(start=m.start(), end=m.end()),
            zitat=m.group(),
        )
        for m in VAGE.finditer(quelle)
    ]


def pruefe_messbarkeit(anforderungen: list[Anforderung]) -> list[Befund]:
    return [
        Befund(
            regel_id="LB202",
            regel_name="fehlende-messgroesse",
            schwere=Schwere.HINWEIS,
            anforderung_id=a.id,
            begruendung="Die Anforderung enthält weder einen Zahlenwert noch einen Normverweis; prüfen, ob ein Angebot eindeutig dagegen geprüft werden kann.",
            rechtsgrundlage=RECHTSGRUNDLAGE,
            span=a.span,
            zitat=a.text,
        )
        for a in anforderungen
        if not MESSBAR.search(a.text)
    ]
