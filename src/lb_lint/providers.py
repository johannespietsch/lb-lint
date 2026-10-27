"""The single LLM chokepoint (T2). Every call to a model provider goes through `aufruf`.

The provider is chosen by `LB_LINT_MODELL` (pydantic-ai model string). Mistral is the
target (D-001); Anthropic is the interim development provider (D-010).
"""

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from decimal import Decimal

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models import Model

from lb_lint.models import LlmAufruf

load_dotenv()
os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")
log = logging.getLogger(__name__)

STANDARD_MODELL = "anthropic:claude-haiku-5-5"
STANDARD_EFFORT = "low"

# USD per 1M tokens (input, output). Source: Claude API reference, as of 2026-10-06.
# Haiku 5.5 prices apply to prompts up to 100K tokens; longer prompts cost more.
PREISE_USD: dict[str, tuple[Decimal, Decimal]] = {
    "claude-haiku-5-5": (Decimal("0.10"), Decimal("0.50")),
    "claude-sonnet-5-5": (Decimal("2.00"), Decimal("10.00")),
}
PREISE_USD_LANGER_PROMPT: dict[str, tuple[Decimal, Decimal]] = {
    "claude-haiku-5-5": (Decimal("0.50"), Decimal("2.50")),
}
LANGER_PROMPT_AB = 100_000

# ECB reference rate of 2026-10-26: 1 EUR = 1.1188 USD. Fixed so costs are reproducible.
USD_PRO_EUR = Decimal("1.1188")


def kosten_eur(model_id: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Cost of one call in EUR. Unknown models raise: a cost of 0 would be a silent lie."""
    tabelle = PREISE_USD_LANGER_PROMPT if input_tokens > LANGER_PROMPT_AB else PREISE_USD
    if model_id not in tabelle:
        tabelle = PREISE_USD
    if model_id not in tabelle:
        raise KeyError(f"no price for model {model_id!r}; add it to PREISE_USD")
    preis_in, preis_out = tabelle[model_id]
    usd = (preis_in * input_tokens + preis_out * output_tokens) / 1_000_000
    return (usd / USD_PRO_EUR).quantize(Decimal("0.000001"))


def aufruf[T: BaseModel](
    system: str,
    nutzer: str,
    output_type: type[T],
    modell: str | Model | None = None,
    effort: str | None = STANDARD_EFFORT,
) -> tuple[T, LlmAufruf]:
    """Run one structured LLM call and return its output with an audit entry.

    `system` is trusted; `nutzer` carries untrusted document text (T1) and is never
    interpolated into `system`. Output uses the provider's native structured output.
    """
    modell = modell or os.environ.get("LB_LINT_MODELL", STANDARD_MODELL)
    settings = {"anthropic_effort": effort} if effort else {}
    agent = Agent(modell, output_type=NativeOutput(output_type), instructions=system)

    zeitpunkt = datetime.now(UTC)
    ergebnis = agent.run_sync(nutzer, model_settings=settings)
    usage = ergebnis.usage

    model_id = agent.model.model_name
    eintrag = LlmAufruf(
        model_id=model_id,
        prompt_sha256=_prompt_hash(model_id, system, nutzer, settings, output_type),
        effort=effort,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_eur=kosten_eur(model_id, usage.input_tokens, usage.output_tokens),
        timestamp=zeitpunkt,
    )
    log.info("%s: %d in / %d out, %s EUR", model_id, eintrag.input_tokens, eintrag.output_tokens, eintrag.cost_eur)
    return ergebnis.output, eintrag


def _prompt_hash(model_id: str, system: str, nutzer: str, settings: dict, output_type: type[BaseModel]) -> str:
    """Hash of everything that determines the request, including the output schema."""
    inhalt = {
        "model": model_id,
        "system": system,
        "nutzer": nutzer,
        "settings": settings,
        "schema": output_type.model_json_schema(),
    }
    return hashlib.sha256(json.dumps(inhalt, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
