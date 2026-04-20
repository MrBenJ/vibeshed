"""``vibeshed validate`` — lint registry.yaml and job folder structure."""

from __future__ import annotations

import typer

from vibeshed.commands._common import SLUG_PATTERN, find_project_root, load_registry


def validate() -> None:
    """Check that registry entries and job folders are well-formed."""
    project_root = find_project_root()
    registry = load_registry(project_root)
    errors: list[str] = []
    warnings: list[str] = []

    if "version" not in registry:
        warnings.append("registry.yaml is missing a top-level `version` field.")

    jobs = registry.get("jobs") or {}
    seen_dirs: set[str] = set()

    for slug, entry in jobs.items():
        if not SLUG_PATTERN.match(slug):
            errors.append(f"Job key {slug!r} is not a valid kebab-case slug.")
        if not isinstance(entry, dict):
            errors.append(f"Job {slug!r} entry must be a mapping.")
            continue
        if entry.get("slug") and entry["slug"] != slug:
            errors.append(
                f"Job {slug!r} has mismatched inner slug {entry['slug']!r}."
            )
        for required in ("name", "description"):
            if not entry.get(required):
                warnings.append(f"Job {slug!r} is missing `{required}`.")

        job_dir = project_root / "jobs" / slug
        seen_dirs.add(slug)
        if not job_dir.is_dir():
            errors.append(f"Job {slug!r} has no folder at {job_dir.relative_to(project_root)}.")
            continue
        for required_file in ("config.yaml", "sequence.md", "scripts/main.py"):
            if not (job_dir / required_file).exists():
                errors.append(
                    f"Job {slug!r} is missing {required_file}."
                )

    jobs_root = project_root / "jobs"
    if jobs_root.is_dir():
        for child in jobs_root.iterdir():
            if child.is_dir() and child.name not in seen_dirs:
                warnings.append(
                    f"Job folder `jobs/{child.name}` exists but is not registered in registry.yaml."
                )

    for warning in warnings:
        typer.secho(f"warning: {warning}", fg=typer.colors.YELLOW)
    for error in errors:
        typer.secho(f"error:   {error}", fg=typer.colors.RED)

    if errors:
        typer.secho(f"\n{len(errors)} error(s), {len(warnings)} warning(s).", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    typer.secho(
        f"OK — {len(jobs)} job(s) validated, {len(warnings)} warning(s).",
        fg=typer.colors.GREEN,
    )
