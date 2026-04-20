"""Typer entry point — wires commands to the ``vibeshed`` console script."""

from __future__ import annotations

import typer

from vibeshed import __version__
from vibeshed.commands.doctor import doctor
from vibeshed.commands.eject import eject
from vibeshed.commands.init import init
from vibeshed.commands.list_cmd import list_jobs
from vibeshed.commands.logs import logs
from vibeshed.commands.new import new
from vibeshed.commands.run import run
from vibeshed.commands.status import status
from vibeshed.commands.update import update
from vibeshed.commands.validate import validate

app = typer.Typer(
    add_completion=False,
    help="VibeShed — vibe coding framework for personal automations.",
    no_args_is_help=True,
)

app.command("init")(init)
app.command("update")(update)
app.command("status")(status)
app.command("new")(new)
app.command("run")(run)
app.command("list")(list_jobs)
app.command("validate")(validate)
app.command("logs")(logs)
app.command("doctor")(doctor)
app.command("eject")(eject)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"vibeshed {__version__}")
        raise typer.Exit()


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """VibeShed CLI."""
