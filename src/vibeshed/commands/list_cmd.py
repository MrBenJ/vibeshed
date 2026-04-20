"""``vibeshed list`` — print registered jobs and their last run."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from vibeshed.commands._common import find_project_root, load_registry


def list_jobs() -> None:
    """List every job in registry.yaml with its last-run status."""
    project_root = find_project_root()
    registry = load_registry(project_root)

    table = Table(title="VibeShed jobs", show_lines=False)
    table.add_column("Slug", style="cyan")
    table.add_column("Name")
    table.add_column("Tags", style="dim")
    table.add_column("Last run", style="dim")
    table.add_column("Status")

    if not registry["jobs"]:
        Console().print(table)
        typer.echo("No jobs yet. Create one with `vibeshed new <slug>`.")
        return

    for slug, entry in sorted(registry["jobs"].items()):
        last_run, last_status = _last_run(project_root, slug)
        table.add_row(
            slug,
            entry.get("name", ""),
            entry.get("tags", "") or "",
            last_run or "—",
            _color_status(last_status) if last_status else "—",
        )
    Console().print(table)


def _last_run(project_root: Path, slug: str) -> tuple[str | None, str | None]:
    runs_file = project_root / "logs" / slug / "runs.json"
    if not runs_file.exists():
        return None, None
    data = json.loads(runs_file.read_text(encoding="utf-8"))
    runs = data.get("runs", {})
    if not runs:
        return None, None
    latest_ts = max(runs.keys())
    return latest_ts, runs[latest_ts].get("status")


def _color_status(status: str) -> str:
    if status == "SUCCESS":
        return "[green]SUCCESS[/green]"
    if status == "FAILURE":
        return "[red]FAILURE[/red]"
    return f"[yellow]{status}[/yellow]"
