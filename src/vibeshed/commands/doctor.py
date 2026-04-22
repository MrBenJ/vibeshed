"""``vibeshed doctor`` — environment and structure health check."""

from __future__ import annotations

import os
import shutil
import sys

import typer

from vibeshed import __version__, manifest as manifest_mod
from vibeshed.commands._common import (
    VENV_PYTHON_ENV,
    find_project_root,
    load_registry,
    project_venv_python,
    resolve_python_interpreter,
)


def doctor() -> None:
    """Check Python version, git availability, env vars declared in registry."""
    project_root = find_project_root()
    typer.echo(f"VibeShed {__version__}")
    typer.echo(f"Project: {project_root}")
    typer.echo("")

    issues = 0

    py_version = sys.version_info
    if py_version < (3, 9):
        typer.secho(
            f"  ✗ Python {py_version.major}.{py_version.minor} found; need >= 3.9",
            fg=typer.colors.RED,
        )
        issues += 1
    else:
        typer.secho(f"  ✓ Python {py_version.major}.{py_version.minor}", fg=typer.colors.GREEN)

    if shutil.which("git"):
        typer.secho("  ✓ git available (needed for `vibeshed update`)", fg=typer.colors.GREEN)
    else:
        typer.secho("  ✗ git not on PATH (required for `vibeshed update`)", fg=typer.colors.RED)
        issues += 1

    manifest = manifest_mod.load(project_root)
    if manifest is None:
        typer.secho("  ✗ .vibeshed/manifest.json missing", fg=typer.colors.RED)
        issues += 1
    else:
        typer.secho(
            f"  ✓ Framework version recorded: {manifest.framework_version}",
            fg=typer.colors.GREEN,
        )

    requirements_path = project_root / "requirements.txt"
    venv_python = project_venv_python(project_root)
    override = os.getenv(VENV_PYTHON_ENV)
    interpreter = resolve_python_interpreter(project_root)
    if override:
        typer.secho(
            f"  ✓ Using {VENV_PYTHON_ENV}={override} to run jobs", fg=typer.colors.GREEN
        )
    elif venv_python is not None:
        typer.secho(f"  ✓ Project .venv detected: {venv_python}", fg=typer.colors.GREEN)
    elif requirements_path.exists():
        typer.secho(
            "  ⚠ requirements.txt exists but no .venv was found. Jobs will run with "
            f"{interpreter}, which likely does not see project dependencies. "
            "Create one with: uv venv && uv pip install -r requirements.txt "
            f"(or set {VENV_PYTHON_ENV} to an interpreter that has them).",
            fg=typer.colors.YELLOW,
        )
    else:
        typer.secho(
            f"  ✓ No requirements.txt; jobs will run with {interpreter}",
            fg=typer.colors.GREEN,
        )

    typer.echo("")
    typer.echo("Environment variables declared in registry.yaml:")
    registry = load_registry(project_root)
    declared: set[str] = set()
    for entry in registry.get("jobs", {}).values():
        for var in (entry.get("dependencies") or {}).get("env_vars") or []:
            declared.add(var)

    if not declared:
        typer.echo("  (none declared)")
    for var in sorted(declared):
        if os.getenv(var):
            typer.secho(f"  ✓ {var}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ⚠ {var} — not set", fg=typer.colors.YELLOW)

    if issues:
        typer.secho(f"\n{issues} issue(s) found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    typer.secho("\nAll core checks passed.", fg=typer.colors.GREEN)
