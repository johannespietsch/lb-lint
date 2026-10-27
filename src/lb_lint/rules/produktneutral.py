"""§ 31 Abs. 6 VgV: references to brands and product types (D-007).

LB101: brand/type reference without "oder gleichwertig" / "oder vergleichbar" in the
same sentence window. LB102: with the addition — still a hint, because the reference
must also be justified by the subject matter, which a rule cannot see.
"""

import re

from lb_lint.models import Befund, Schwere, Span

RECHTSGRUNDLAGE = "§ 31 Abs. 6 VgV"

# Brands and product types for IT procurement. The pattern tries longer names first,
# so "Intel Core i5" wins over "Intel". Interface standards (USB, HDMI, Bluetooth,
# Wi-Fi) are deliberately absent: they are standards, not references to a manufacturer.
# Eco labels (TCO Certified, Blauer Engel) fall under § 34 VgV and are out of scope.
GAZETTEER = [
    "Microsoft Windows", "Microsoft Office", "Microsoft 365", "Microsoft Teams", "Microsoft Intune",
    "Intel Core i3", "Intel Core i5", "Intel Core i7", "Intel Core i9", "Intel Core", "Intel Xeon", "Intel Celeron", "Intel Pentium", "AMD Ryzen",
    "Apple MacBook", "Surface Pro", "Surface Laptop", "Surface Go",
    "Dell", "Lenovo", "Hewlett-Packard", "HP", "Apple", "Acer", "Asus", "Fujitsu", "Samsung",
    "Toshiba", "Dynabook", "Panasonic", "Microsoft", "Intel", "AMD", "Qualcomm", "NVIDIA",
    "ThinkPad", "ThinkCentre", "Latitude", "EliteBook", "ProBook", "MacBook", "iPad", "Chromebook",
    "Toughbook", "Core i3", "Core i5", "Core i7", "Core i9", "Xeon", "Ryzen", "Snapdragon", "GeForce",
    "Thunderbolt", "Windows", "macOS", "iPadOS", "ChromeOS", "Office", "Adobe", "Acrobat",
    "Logitech", "Cisco", "Jamf", "Intune",
]

MARKE = re.compile(r"(?<![\w])(?:" + "|".join(re.escape(m) for m in sorted(GAZETTEER, key=len, reverse=True)) + r")(?![\w])")
ZUSATZ = re.compile(r"\boder\s+(?:gleichwertig|vergleichbar)\w*", re.IGNORECASE)
NUR_LUECKE = re.compile(r"[\s-]*")


def pruefe(quelle: str, fenster: list[Span]) -> list[Befund]:
    befunde = []
    for f in fenster:
        satz = quelle[f.start : f.end]
        mit_zusatz = ZUSATZ.search(satz) is not None
        for start, ende in _zusammengefasst(MARKE.finditer(satz)):
            span = Span(start=f.start + start, end=f.start + ende)
            zitat = quelle[span.start : span.end]
            befunde.append(
                Befund(
                    regel_id="LB102" if mit_zusatz else "LB101",
                    regel_name="produktneutralitaet-begruendung-pruefen" if mit_zusatz else "produktneutralitaet-verletzt",
                    schwere=Schwere.HINWEIS if mit_zusatz else Schwere.FEHLER,
                    anforderung_id=None,
                    begruendung=(
                        f"Verweis auf „{zitat}“ mit Gleichwertigkeitszusatz. Zulässig nur, wenn der "
                        "Auftragsgegenstand anders nicht hinreichend genau beschrieben werden kann; "
                        "Begründung prüfen und dokumentieren."
                        if mit_zusatz
                        else f"Verweis auf „{zitat}“ ohne den Zusatz „oder gleichwertig“."
                    ),
                    rechtsgrundlage=RECHTSGRUNDLAGE,
                    span=span,
                    zitat=zitat,
                )
            )
    return befunde


def _zusammengefasst(treffer) -> list[tuple[int, int]]:
    """Merge adjacent names ("Microsoft Windows", "Intel Core i5") into one span."""
    bereiche: list[tuple[int, int]] = []
    for m in treffer:
        if bereiche and NUR_LUECKE.fullmatch(m.string[bereiche[-1][1] : m.start()]):
            bereiche[-1] = (bereiche[-1][0], m.end())
        else:
            bereiche.append((m.start(), m.end()))
    return bereiche
