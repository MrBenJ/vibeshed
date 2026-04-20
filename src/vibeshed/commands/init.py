"""``vibeshed init`` — scaffold a new VibeShed project."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from vibeshed import cache, manifest as manifest_mod
from vibeshed.templates_loader import (
    INIT_DIRECTORIES,
    MANAGED_FILES,
    UNMANAGED_INIT_FILES,
    template_text,
)


def init(
    path: Optional[Path] = typer.Argument(
        None,
        help="Directory to create. Defaults to the current directory.",
    ),
) -> None:
    """Scaffold a new VibeShed project at PATH (or in the current directory)."""
    target = (path or Path(".")).resolve()
    target.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_mod.manifest_path(target)
    if manifest_path.exists():
        typer.secho(
            f"VibeShed manifest already exists at {manifest_path}. "
            "Run `vibeshed update` to pull the latest framework files.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    written: list[str] = []

    for rel_path in (*MANAGED_FILES.keys(), *UNMANAGED_INIT_FILES):
        body = template_text(rel_path)
        dest = target / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        written.append(rel_path)
        if rel_path in MANAGED_FILES:
            cache.write(target, rel_path, body)

    for directory in INIT_DIRECTORIES:
        (target / directory).mkdir(parents=True, exist_ok=True)
        keep = target / directory / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    manifest_mod.save(target, manifest_mod.fresh_manifest())

    typer.secho(f"Initialized VibeShed project at {target}", fg=typer.colors.GREEN)
    typer.echo(f"  {len(written)} files written, {len(INIT_DIRECTORIES)} directories created.")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo(f"  cd {target}")
    typer.echo("  vibeshed new my-first-job")
    typer.echo("  vibeshed run my-first-job")
