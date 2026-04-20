"""``vibeshed status`` — show framework version and managed-file drift."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from vibeshed import __version__, manifest as manifest_mod
from vibeshed.commands._common import find_project_root
from vibeshed.templates_loader import MANAGED_FILES, template_bytes


def status() -> None:
    """Show installed version, available version, and per-file drift state."""
    project_root = find_project_root()
    manifest = manifest_mod.load(project_root)
    if manifest is None:
        typer.secho("No manifest found. Run `vibeshed init` first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Project:           {project_root}")
    typer.echo(f"Installed version: {manifest.framework_version}")
    typer.echo(f"Available version: {__version__}")

    table = Table(title="Managed files", show_lines=False)
    table.add_column("File", style="cyan")
    table.add_column("Mode", style="dim")
    table.add_column("Local")
    table.add_column("Upstream")

    for rel, mode in MANAGED_FILES.items():
        local_path = project_root / rel
        if not local_path.exists():
            table.add_row(rel, mode, "[red]missing[/red]", "—")
            continue
        local_sha = manifest_mod.sha256_file(local_path)
        recorded_sha = manifest.files.get(rel).sha if rel in manifest.files else None
        upstream_sha = manifest_mod.sha256_bytes(template_bytes(rel))

        local_state = "clean" if local_sha == recorded_sha else "[yellow]modified[/yellow]"
        upstream_state = "same" if recorded_sha == upstream_sha else "[blue]update available[/blue]"
        table.add_row(rel, mode, local_state, upstream_state)

    Console().print(table)
