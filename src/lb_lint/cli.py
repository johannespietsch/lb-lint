"""Command line: `lb-lint pruefe <datei>`."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from lb_lint.models import Schwere
from lb_lint.pipeline import pruefe_dokument

app = typer.Typer(no_args_is_help=True, help="Ein Linter für Leistungsbeschreibungen. Kein Rechtsrat.")


@app.callback()
def _main() -> None:
    """Keeps `pruefe` a subcommand even while it is the only one."""


FARBE = {Schwere.FEHLER: "red", Schwere.WARNUNG: "yellow", Schwere.HINWEIS: "cyan"}


@app.command()
def pruefe(
    datei: Path = typer.Argument(..., exists=True, dir_okay=False, help="Leistungsbeschreibung als .md oder .txt"),
    als_json: bool = typer.Option(False, "--json", help="Anforderungen und Befunde als JSON ausgeben"),
    protokoll: Path = typer.Option(Path("pruefprotokoll.json"), help="Pfad für das Prüfprotokoll"),
    tenant: str = typer.Option("default", help="Mandant (T4)"),
) -> None:
    """Prüft eine Leistungsbeschreibung. Exit-Code 1, wenn mindestens ein Befund der Schwere 'fehler' vorliegt."""
    quelle = datei.read_text(encoding="utf-8")
    p = pruefe_dokument(quelle, tenant_id=tenant)
    protokoll.write_text(p.protokoll.model_dump_json(indent=2), encoding="utf-8")

    labels = {a.id: a.label for a in p.anforderungen}
    if als_json:
        ausgabe = {
            "anforderungen": [a.model_dump(mode="json") for a in p.anforderungen],
            "befunde": [b.model_dump(mode="json") for b in p.befunde],
        }
        print(json.dumps(ausgabe, ensure_ascii=False, indent=2))
    else:
        konsole = Console()
        tabelle = Table(title=f"{datei.name}: {len(p.anforderungen)} Anforderungen, {len(p.befunde)} Befunde")
        for spalte in ("Anforderung", "Regel", "Schwere", "Zitat", "Rechtsgrundlage"):
            tabelle.add_column(spalte)
        for b in p.befunde:
            tabelle.add_row(
                labels.get(b.anforderung_id, "–"),
                f"{b.regel_id} {b.regel_name}",
                f"[{FARBE[b.schwere]}]{b.schwere}[/]",
                b.zitat if len(b.zitat) <= 60 else b.zitat[:57] + "…",
                b.rechtsgrundlage,
            )
        konsole.print(tabelle)
        pp = p.protokoll
        konsole.print(
            f"Prüfprotokoll: {protokoll} · {pp.aufrufe[0].model_id if pp.aufrufe else '–'} · "
            f"{pp.input_tokens}/{pp.output_tokens} Tokens · {pp.cost_eur} EUR · "
            f"Offsets repariert {pp.offset_repariert}, verworfen {pp.offset_verworfen}"
        )
        konsole.print("[dim]lb-lint ist ein Linter, keine Rechtsberatung. Jeder Befund ist ein Vorschlag zur Prüfung.[/]")

    raise typer.Exit(1 if any(b.schwere is Schwere.FEHLER for b in p.befunde) else 0)
