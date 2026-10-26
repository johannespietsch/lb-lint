from pathlib import Path

from lb_lint.segment import abschnitte

SAMPLE = (Path(__file__).parents[1] / "samples" / "laptops_schulen.md").read_text()


def test_sample_sections_match_visible_numbering():
    teile = abschnitte(SAMPLE)
    assert [a.nummer for a in teile] == [0, 1, 2, 3, 4, 5, 6]
    assert teile[0].titel == "Präambel"
    assert teile[1].titel == "1. Gegenstand der Leistung"
    assert SAMPLE[teile[0].span.start : teile[0].span.end].startswith("# Leistungsbeschreibung")


def test_sections_are_contiguous_and_cover_document():
    teile = abschnitte(SAMPLE)
    assert teile[0].span.start == 0
    assert teile[-1].span.end == len(SAMPLE)
    for a, b in zip(teile, teile[1:]):
        assert a.span.end == b.span.start


def test_lower_level_headings_stay_in_parent():
    text = "## A\nx\n### A.1\ny\n## B\nz\n"
    teile = abschnitte(text)
    assert [a.titel for a in teile] == ["A", "B"]
    assert "### A.1" in text[teile[0].span.start : teile[0].span.end]


def test_blank_preamble_is_dropped():
    assert [a.nummer for a in abschnitte("\n\n## A\nx\n## B\ny\n")] == [1, 2]


def test_no_headings_is_one_preamble():
    teile = abschnitte("Nur Text.\n")
    assert [(a.nummer, a.span.end) for a in teile] == [(0, 10)]
    assert abschnitte("   \n") == []


def test_tie_prefers_higher_level():
    assert [a.titel for a in abschnitte("# A\nx\n## A.1\ny\n")] == ["A"]


def test_closing_hashes_are_stripped():
    assert abschnitte("## Titel ##\nx\n")[0].titel == "Titel"
