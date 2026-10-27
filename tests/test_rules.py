"""Rule checks: no LLM, fast, deterministic (D-003)."""

from pathlib import Path

from lb_lint.models import Anforderung, Kategorie, Span
from lb_lint.rules import pruefe

SAMPLE = (Path(__file__).parents[1] / "samples" / "laptops_schulen.md").read_text()


def regeln(text: str, anforderungen=()) -> list[tuple[str, str]]:
    return [(b.regel_id, b.zitat) for b in pruefe(text, list(anforderungen))]


def anforderung(text: str, quelle: str) -> Anforderung:
    start = quelle.index(text)
    return Anforderung(
        id="0" * 12, label="A-1-1", text=text, span=Span(start=start, end=start + len(text)),
        abschnitt=1, kategorie=Kategorie.TECHNISCH, messbar=False,
    )


def test_brand_without_addition_is_an_error():
    assert regeln("Die Geräte sind von Dell zu liefern.") == [("LB101", "Dell")]


def test_brand_with_addition_is_a_hint():
    assert regeln("Geräte von Dell oder gleichwertig.") == [("LB102", "Dell")]
    assert regeln("Ein Dock von Lenovo oder vergleichbar.") == [("LB102", "Lenovo")]  # D-007


def test_addition_in_neighbouring_sentence_does_not_count():
    assert regeln("Geräte von Dell. Andere Geräte oder gleichwertig.") == [("LB101", "Dell")]
    assert regeln("Gemäß § 31 Abs. 6 VgV. Geräte von Dell oder gleichwertig.") == [("LB102", "Dell")]


def test_longest_name_wins_and_adjacent_names_merge():
    assert regeln("Prozessor: Intel Core i5.") == [("LB101", "Intel Core i5")]
    assert regeln("Ein Lenovo ThinkPad.") == [("LB101", "Lenovo ThinkPad")]


def test_standards_and_word_parts_are_not_brands():
    assert regeln("- WLAN nach IEEE 802.11ax, HDMI 2.0, USB-C, Bluetooth 5.1") == []
    assert regeln("Lieferung an das Dellbrücker Rathaus.") == []


def test_vague_terms_any_inflection():
    assert regeln("Eine ausreichende Laufzeit, zeitnah und nach Bedarf.") == [
        ("LB201", "ausreichende"), ("LB201", "zeitnah"), ("LB201", "nach Bedarf"),
    ]


def test_missing_number_or_norm_is_flagged_per_anforderung():
    q = "Das Gehäuse muss robust sein. Ergonomie nach DIN EN ISO 9241. Gewicht unter 2 kg."
    reqs = [anforderung(t, q) for t in ["Das Gehäuse muss robust sein.", "Ergonomie nach DIN EN ISO 9241.", "Gewicht unter 2 kg."]]
    assert regeln(q, reqs) == [("LB202", "Das Gehäuse muss robust sein.")]


def test_findings_attach_to_containing_anforderung():
    q = "Vorwort mit Dell. Prozessor von Intel."
    req = anforderung("Prozessor von Intel.", q)
    befunde = {b.zitat: b.anforderung_id for b in pruefe(q, [req]) if b.regel_id == "LB101"}
    assert befunde == {"Dell": None, "Intel": req.id}


def test_sample_planted_defects():
    """The rule-detectable rows of samples/laptops_schulen.defects.md."""
    gefunden = regeln(SAMPLE)
    assert ("LB101", "Intel Core i5") in gefunden
    assert ("LB101", "Microsoft Office") in gefunden
    assert ("LB102", "Microsoft Windows") in gefunden
    assert ("LB102", "Lenovo ThinkPad") in gefunden
    assert {z for r, z in gefunden if r == "LB201"} == {"ausreichende", "zeitnah", "marktüblicher"}
    assert ("LB101", "Office") in gefunden  # known false positive: "Back-Office" (M4 critique)


def test_every_finding_slices_to_its_quote():
    for b in pruefe(SAMPLE, []):
        assert SAMPLE[b.span.start : b.span.end] == b.zitat


def test_rules_are_deterministic():
    assert pruefe(SAMPLE, []) == pruefe(SAMPLE, [])
