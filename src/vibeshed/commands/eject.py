"""``vibeshed eject`` — stop tracking framework files. No more updates."""

from __future__ import annotations

import shutil

import typer

from vibeshed import manifest as manifest_mod, markers
from vibeshed.commands._common import find_project_root
from vibeshed.templates_loader import MANAGED_FILES


def eject(
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip the confirmation prompt."),
) -> None:
    """Strip vibeshed markers and delete the manifest, leaving content intact."""
    project_root = find_project_root()
    if not yes:
        typer.confirm(
            "Eject this project from VibeShed? Markers will be stripped and "
            "future `vibeshed update` will refuse to run. This is irreversible.",
            abort=True,
        )

    for rel, mode in MANAGED_FILES.items():
        if mode != "marker":
            continue
        path = project_root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text(markers.strip_markers(text), encoding="utf-8")
        typer.echo(f"  stripped markers: {rel}")

    vibeshed_dir = project_root / manifest_mod.MANIFEST_DIR
    if vibeshed_dir.exists():
        shutil.rmtree(vibeshed_dir)
        typer.echo(f"  removed: {vibeshed_dir}")

    typer.secho("Ejected. The repo is fully yours now.", fg=typer.colors.GREEN)
