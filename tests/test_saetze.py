from lb_lint.rules.saetze import fenster


def saetze(text: str) -> list[str]:
    return [text[s.start : s.end] for s in fenster(text)]


def test_statute_name_at_sentence_end_splits():
    # I-001: spaCy kept "VgV." as an abbreviation and merged or misplaced these.
    assert saetze("Ausschluss gemäß § 57 Abs. 1 VgV. Danach folgt Satz zwei.") == [
        "Ausschluss gemäß § 57 Abs. 1 VgV.",
        "Danach folgt Satz zwei.",
    ]
    assert saetze("Es gilt § 121 GWB. Ende.") == ["Es gilt § 121 GWB.", "Ende."]


def test_abbreviations_do_not_split():
    for text in [
        "Nachweis, z. B. durch Vorlage des Zertifikats.",
        "Lieferung gemäß Anlage 2 i. V. m. dem Lieferplan.",
        "Notebooks inkl. Netzteil, ggf. auch im Distanzunterricht.",
        "Siehe Nr. 3 bzw. ca. 1.200 Geräte.",
    ]:
        assert saetze(text) == [text]


def test_ordinal_does_not_split():
    assert saetze("Prozessor: Intel Core i5 der 13. Generation oder gleichwertig.") == [
        "Prozessor: Intel Core i5 der 13. Generation oder gleichwertig."
    ]


def test_list_items_are_hard_boundaries_without_full_stop():
    # I-001: the parser merged two adjacent bullets into one sentence.
    assert saetze("- Massenspeicher: 512 GB\n- Display: 14 Zoll\n") == ["Massenspeicher: 512 GB", "Display: 14 Zoll"]


def test_headings_and_blank_lines_are_boundaries():
    assert saetze("## 2. Technik\n\nText ohne Punkt\n\nNoch einer") == ["2. Technik", "Text ohne Punkt", "Noch einer"]


def test_wrapped_paragraph_line_is_not_a_boundary():
    assert saetze("Die Geräte sind von Dell\noder gleichwertig zu liefern.") == [
        "Die Geräte sind von Dell\noder gleichwertig zu liefern."
    ]


def test_spans_point_into_source():
    text = "  - Erster Satz. Zweiter Satz.\n"
    for s in fenster(text):
        assert text[s.start : s.end].strip() == text[s.start : s.end]
