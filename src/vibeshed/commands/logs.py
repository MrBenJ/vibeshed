"""``vibeshed logs`` — show recent log lines for a job."""

from __future__ import annotations

import typer

from vibeshed.commands._common import find_project_root


def logs(
    slug: str = typer.Argument(..., help="Job slug to show logs for."),
    n: int = typer.Option(50, "-n", "--lines", help="Number of trailing lines to print."),
) -> None:
    """Print the last N lines of the most recent log file for SLUG."""
    project_root = find_project_root()
    slug_logs = project_root / "logs" / slug
    if not slug_logs.is_dir():
        typer.secho(f"No logs yet for {slug!r} (no folder at {slug_logs}).", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    candidates = sorted(slug_logs.rglob("run_*.log"))
    if not candidates:
        typer.secho(f"No log files under {slug_logs}.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    latest = candidates[-1]
    typer.secho(f"# {latest}", fg=typer.colors.CYAN)
    lines = latest.read_text(encoding="utf-8").splitlines()
    for line in lines[-n:]:
        typer.echo(line)
