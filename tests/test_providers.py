from decimal import Decimal

import pytest
from pydantic import BaseModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.profiles import ModelProfile

from lb_lint import providers
from lb_lint.providers import aufruf, kosten_eur


def stub() -> TestModel:
    return TestModel(custom_output_text='{"wert": "x"}', profile=ModelProfile(supports_json_schema_output=True))


class Antwort(BaseModel):
    wert: str


def test_cost_in_eur_uses_fixed_rate():
    # 100K in + 100K out on Haiku 5.5 = 0.01 + 0.05 = 0.06 USD; / 1.1188 = 0.053629 EUR
    assert kosten_eur("claude-haiku-5-5", 100_000, 100_000) == Decimal("0.053629")


def test_long_prompt_tier():
    assert kosten_eur("claude-haiku-5-5", 100_001, 0) > kosten_eur("claude-haiku-5-5", 100_000, 0) * 4


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        kosten_eur("unbekannt", 1, 1)


def test_aufruf_returns_output_and_audit_entry(monkeypatch):
    monkeypatch.setitem(providers.PREISE_USD, "test", (Decimal("1"), Decimal("1")))
    ausgabe, eintrag = aufruf("System", "Dokumenttext", Antwort, modell=stub())
    assert isinstance(ausgabe, Antwort)
    assert eintrag.model_id == "test"
    assert eintrag.temperature is None  # I-002: never claim a setting that was not sent
    assert eintrag.effort == "low"
    assert len(eintrag.prompt_sha256) == 64


def test_prompt_hash_changes_with_input(monkeypatch):
    monkeypatch.setitem(providers.PREISE_USD, "test", (Decimal("1"), Decimal("1")))
    _, a = aufruf("System", "Text A", Antwort, modell=stub())
    _, b = aufruf("System", "Text B", Antwort, modell=stub())
    assert a.prompt_sha256 != b.prompt_sha256
