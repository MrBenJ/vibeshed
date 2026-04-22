"""Shared helpers for command implementations."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml

from vibeshed import manifest as manifest_mod

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

VENV_PYTHON_ENV = "VIBESHED_PYTHON"


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


def project_venv_python(project_root: Path) -> Optional[Path]:
    """Return the project's ``.venv`` interpreter path if it exists, else ``None``."""
    if sys.platform.startswith("win"):
        candidate = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = project_root / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else None


def resolve_python_interpreter(project_root: Path) -> str:
    """Pick the interpreter used to spawn job scripts.

    Priority:
      1. ``$VIBESHED_PYTHON`` — explicit escape hatch.
      2. ``<project_root>/.venv/bin/python`` — the project's own venv, so jobs
         see dependencies installed from ``requirements.txt``.
      3. ``sys.executable`` — the CLI's own interpreter (e.g. the pipx env).
    """
    override = os.getenv(VENV_PYTHON_ENV)
    if override:
        return override
    venv_python = project_venv_python(project_root)
    if venv_python is not None:
        return str(venv_python)
    return sys.executable


def assert_slug(slug: str) -> None:
    if not SLUG_PATTERN.match(slug):
        typer.secho(
            f"Invalid slug: {slug!r}. Use kebab-case: lowercase letters, digits, hyphens; "
            "must start with a letter.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
