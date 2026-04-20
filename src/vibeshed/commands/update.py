"""``vibeshed update`` — pull the latest framework files into a project.

For ``mode: "full"`` files we do a three-way merge against the cached base
content (recorded at last init/update). For ``mode: "marker"`` files we
replace only the in-marker section, preserving everything else.
"""

from __future__ import annotations

import typer

from vibeshed import __version__, cache, manifest as manifest_mod, markers, merger, migrations
from vibeshed.commands._common import find_project_root
from vibeshed.templates_loader import MANAGED_FILES, template_text


def update(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would change without writing."
    ),
) -> None:
    """Update framework-managed files to the version this CLI ships."""
    project_root = find_project_root()
    manifest = manifest_mod.load(project_root)
    if manifest is None:
        typer.secho("No manifest found. Run `vibeshed init` first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if manifest.framework_version == __version__:
        typer.secho(
            f"Already on framework v{__version__}. Nothing to update.",
            fg=typer.colors.GREEN,
        )
        return

    typer.secho(
        f"Updating {manifest.framework_version} → {__version__}"
        + (" [dry run]" if dry_run else ""),
        fg=typer.colors.CYAN,
    )

    summary = {"clean": 0, "user_kept": 0, "merged": 0, "conflicts": [], "marker": 0}
    new_entries: dict[str, manifest_mod.FileEntry] = dict(manifest.files)

    for rel, mode in MANAGED_FILES.items():
        local_path = project_root / rel
        new_text = template_text(rel)
        new_sha = manifest_mod.sha256_bytes(new_text.encode("utf-8"))

        if not local_path.exists():
            _write(local_path, new_text, dry_run)
            cache.write(project_root, rel, new_text)
            new_entries[rel] = manifest_mod.FileEntry(
                sha=new_sha, shipped_in=__version__, mode=mode
            )
            summary["clean"] += 1
            typer.echo(f"  + {rel} (created)")
            continue

        local_text = local_path.read_text(encoding="utf-8")

        if mode == "marker":
            new_managed_body = markers.extract_managed(new_text)
            try:
                merged = markers.replace_managed(local_text, new_managed_body, __version__)
            except markers.MarkerError as exc:
                typer.secho(
                    f"  ! {rel}: {exc}. Skipping (run `vibeshed eject` to detach this file).",
                    fg=typer.colors.YELLOW,
                )
                continue
            if merged != local_text:
                _write(local_path, merged, dry_run)
            cache.write(project_root, rel, new_text)
            new_entries[rel] = manifest_mod.FileEntry(
                sha=manifest_mod.sha256_bytes(merged.encode("utf-8")),
                shipped_in=__version__,
                mode=mode,
            )
            summary["marker"] += 1
            typer.echo(f"  ~ {rel} (managed section refreshed)")
            continue

        recorded = manifest.files.get(rel)
        recorded_sha = recorded.sha if recorded else None
        local_sha = manifest_mod.sha256_bytes(local_text.encode("utf-8"))

        if local_sha == recorded_sha:
            _write(local_path, new_text, dry_run)
            cache.write(project_root, rel, new_text)
            new_entries[rel] = manifest_mod.FileEntry(
                sha=new_sha, shipped_in=__version__, mode=mode
            )
            summary["clean"] += 1
            typer.echo(f"  ✓ {rel}")
            continue

        if recorded_sha == new_sha:
            new_entries[rel] = manifest_mod.FileEntry(
                sha=local_sha, shipped_in=__version__, mode=mode
            )
            summary["user_kept"] += 1
            typer.echo(f"  · {rel} (kept your changes; no upstream change)")
            continue

        base_text = cache.read(project_root, rel)
        if base_text is None:
            typer.secho(
                f"  ! {rel}: no cached base; cannot three-way merge. Skipping.",
                fg=typer.colors.YELLOW,
            )
            continue

        result = merger.merge(local=local_text, base=base_text, remote=new_text)
        _write(local_path, result.text, dry_run)
        cache.write(project_root, rel, new_text)
        new_entries[rel] = manifest_mod.FileEntry(
            sha=manifest_mod.sha256_bytes(result.text.encode("utf-8")),
            shipped_in=__version__,
            mode=mode,
        )
        if result.had_conflict:
            summary["conflicts"].append(rel)
            typer.secho(f"  ✗ {rel} (CONFLICT — resolve markers)", fg=typer.colors.RED)
        else:
            summary["merged"] += 1
            typer.secho(f"  ⊕ {rel} (merged)", fg=typer.colors.BLUE)

    applied = []
    if not dry_run:
        applied = migrations.apply(project_root, manifest.framework_version, __version__)
        manifest_mod.save(
            project_root,
            manifest_mod.Manifest(framework_version=__version__, files=new_entries),
        )

    typer.echo("")
    typer.secho(
        f"Summary: {summary['clean']} clean, {summary['user_kept']} kept, "
        f"{summary['merged']} merged, {summary['marker']} marker, "
        f"{len(summary['conflicts'])} conflict(s)",
        fg=typer.colors.CYAN,
    )
    if applied:
        typer.echo(f"Migrations applied: {', '.join(applied)}")
    if summary["conflicts"]:
        typer.secho(
            "Resolve conflict markers in: " + ", ".join(summary["conflicts"]),
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)


def _write(path, text: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
