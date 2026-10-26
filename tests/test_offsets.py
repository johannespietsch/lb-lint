from lb_lint.offsets import Treffer, lokalisiere

QUELLE = "Gewicht: höchstens 1,5 kg.\nAkku: mindestens\n  8 Stunden.\nGewicht: höchstens 1,5 kg."


def test_exact_match_uses_absolute_offset():
    f = lokalisiere("höchstens 1,5 kg", QUELLE, offset=100, belegt=set())
    assert f.treffer is Treffer.EXAKT
    assert QUELLE[f.span.start - 100 : f.span.end - 100] == "höchstens 1,5 kg"


def test_duplicates_are_assigned_in_order():
    belegt: set[int] = set()
    erste = lokalisiere("Gewicht: höchstens 1,5 kg.", QUELLE, 0, belegt)
    belegt.add(erste.span.start)
    zweite = lokalisiere("Gewicht: höchstens 1,5 kg.", QUELLE, 0, belegt)
    assert erste.span.start == 0
    assert zweite.span.start > erste.span.start
    belegt.add(zweite.span.start)
    assert lokalisiere("Gewicht: höchstens 1,5 kg.", QUELLE, 0, belegt) is None


def test_whitespace_drift_is_repaired_to_original_span():
    f = lokalisiere("Akku: mindestens 8 Stunden.", QUELLE, 0, set())
    assert f.treffer is Treffer.REPARIERT
    assert QUELLE[f.span.start : f.span.end] == "Akku: mindestens\n  8 Stunden."


def test_surrounding_whitespace_in_quote_is_ignored():
    assert lokalisiere("  höchstens 1,5 kg \n", QUELLE, 0, set()).treffer is Treffer.EXAKT


def test_paraphrase_is_rejected():
    assert lokalisiere("Gewicht: max. 1,5 kg.", QUELLE, 0, set()) is None
    assert lokalisiere("Akku: mindestens acht Stunden.", QUELLE, 0, set()) is None


def test_empty_quote_is_rejected():
    assert lokalisiere("   ", QUELLE, 0, set()) is None
