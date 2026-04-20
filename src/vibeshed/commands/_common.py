"""Shared helpers for command implementations."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
import yaml

from vibeshed import manifest as manifest_mod

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def find_project_root(start: Optional[Path] = None) -> Path:
    """Walk upward looking for ``.vibeshed/manifest.json``. Errors if not found."""
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / manifest_mod.MANIFEST_DIR / manifest_mod.MANIFEST_FILENAME).exists():
            return candidate
    typer.secho(
        "Not in a VibeShed project (no .vibeshed/manifest.json found upward from "
        f"{start}). Run `vibeshed init` first.",
        fg=typer.colors.RED,
        err=True,
    )
    raise typer.Exit(code=1)


def load_registry(project_root: Path) -> dict:
    path = project_root / "registry.yaml"
    if not path.exists():
        typer.secho(f"registry.yaml not found at {path}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "jobs" not in data or not isinstance(data["jobs"], dict):
        data["jobs"] = {}
    return data


def save_registry(project_root: Path, data: dict) -> None:
    path = project_root / "registry.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def assert_slug(slug: str) -> None:
    if not SLUG_PATTERN.match(slug):
        typer.secho(
            f"Invalid slug: {slug!r}. Use kebab-case: lowercase letters, digits, hyphens; "
            "must start with a letter.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
