"""``vibeshed new`` — scaffold a new job inside a VibeShed project."""

from __future__ import annotations

import typer

from vibeshed.commands._common import (
    assert_slug,
    find_project_root,
    load_registry,
    save_registry,
)
from vibeshed.templates_loader import iter_job_template_files


def new(
    slug: str = typer.Argument(..., help="Kebab-case slug for the new job."),
    name: str = typer.Option(
        None,
        "--name",
        "-n",
        help="Human-readable job name. Defaults to a Title-Cased version of the slug.",
    ),
) -> None:
    """Create a new job folder from the template and register it."""
    assert_slug(slug)
    project_root = find_project_root()
    job_dir = project_root / "jobs" / slug

    if job_dir.exists():
        typer.secho(f"Job already exists at {job_dir}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    display_name = name or " ".join(part.capitalize() for part in slug.split("-"))

    for rel, body in iter_job_template_files():
        rendered = body.replace("{{JOB_SLUG}}", slug).replace("{{JOB_NAME}}", display_name)
        dest = job_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")

    registry = load_registry(project_root)
    registry["jobs"][slug] = {
        "slug": slug,
        "name": display_name,
        "description": f"TODO: describe what {slug} does.",
        "tags": "",
        "dependencies": {"env_vars": [], "shared_utils": []},
    }
    save_registry(project_root, registry)

    typer.secho(f"Created job {slug} at {job_dir}", fg=typer.colors.GREEN)
    typer.echo("Next steps:")
    typer.echo(f"  $EDITOR {job_dir / 'sequence.md'}")
    typer.echo(f"  $EDITOR {job_dir / 'scripts' / 'main.py'}")
    typer.echo(f"  vibeshed run {slug}")
