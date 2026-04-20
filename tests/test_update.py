"""Tests for ``vibeshed update`` — clean, user-kept, merge, conflict, marker."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vibeshed import cache, manifest as manifest_mod
from vibeshed.cli import app
from vibeshed.commands.update import update as update_cmd


def _bump_version_to(monkeypatch, version: str) -> None:
    """Pretend the CLI was upgraded to a newer framework version."""
    import vibeshed
    import vibeshed.cli
    import vibeshed.commands.update as upd

    monkeypatch.setattr(vibeshed, "__version__", version)
    monkeypatch.setattr(vibeshed.cli, "__version__", version)
    monkeypatch.setattr(upd, "__version__", version)


def _write_template_for(monkeypatch, rel: str, new_text: str) -> None:
    """Stub template_text() so update() sees fresh content for one file."""
    from vibeshed import commands

    real = commands.update.template_text

    def fake(path: str) -> str:
        return new_text if path == rel else real(path)

    monkeypatch.setattr(commands.update, "template_text", fake)


def test_update_no_op_when_versions_match(
    initialized_project: Path, runner: CliRunner
) -> None:
    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert "nothing to update" in result.output.lower()


def test_update_clean_overwrite_for_untouched_file(
    initialized_project: Path, runner: CliRunner, monkeypatch
) -> None:
    rel = "shared/state.py"
    new_content = "# brand new state.py contents\n"
    _bump_version_to(monkeypatch, "0.99.0")
    _write_template_for(monkeypatch, rel, new_content)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0, result.output
    assert (initialized_project / rel).read_text() == new_content


def test_update_keeps_user_changes_when_upstream_unchanged(
    initialized_project: Path, runner: CliRunner, monkeypatch
) -> None:
    rel = "shared/notifications.py"
    user_text = "# user wrote this\n"
    (initialized_project / rel).write_text(user_text, encoding="utf-8")

    _bump_version_to(monkeypatch, "0.99.0")
    # Note: not stubbing template_text means the bundled (unchanged) content is used.

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0, result.output
    assert (initialized_project / rel).read_text() == user_text


def test_update_three_way_merge_clean(
    initialized_project: Path, runner: CliRunner, monkeypatch
) -> None:
    rel = "shared/state.py"
    base_text = (initialized_project / rel).read_text()
    user_text = base_text + "\n# user appended\n"
    upstream_text = "# upstream prepended\n" + base_text

    (initialized_project / rel).write_text(user_text, encoding="utf-8")
    _bump_version_to(monkeypatch, "0.99.0")
    _write_template_for(monkeypatch, rel, upstream_text)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0, result.output

    merged = (initialized_project / rel).read_text()
    assert "# user appended" in merged
    assert "# upstream prepended" in merged


def test_update_conflict_leaves_markers(
    initialized_project: Path, runner: CliRunner, monkeypatch
) -> None:
    rel = "shared/notifications.py"
    base = "line A\nline B\nline C\n"
    cache.write(initialized_project, rel, base)
    (initialized_project / rel).write_text("line A\nUSER LINE\nline C\n", encoding="utf-8")

    _bump_version_to(monkeypatch, "0.99.0")
    _write_template_for(monkeypatch, rel, "line A\nUPSTREAM LINE\nline C\n")

    # Re-record manifest so the recorded SHA matches the cache content above.
    m = manifest_mod.load(initialized_project)
    assert m is not None
    m.files[rel].sha = manifest_mod.sha256_bytes(base.encode("utf-8"))
    manifest_mod.save(initialized_project, m)

    result = runner.invoke(app, ["update"])
    assert result.exit_code != 0
    merged = (initialized_project / rel).read_text()
    assert "<<<<<<<" in merged
    assert ">>>>>>>" in merged


def test_update_marker_mode_preserves_user_content(
    initialized_project: Path, runner: CliRunner, monkeypatch
) -> None:
    agents_path = initialized_project / "AGENTS.md"
    text = agents_path.read_text(encoding="utf-8")
    text += "\n## My personal additions\n\nDo the thing my way.\n"
    agents_path.write_text(text, encoding="utf-8")

    new_template = (
        "<!-- vibeshed:managed:start v0.99.0 -->\n"
        "Brand new managed content\n"
        "<!-- vibeshed:managed:end -->\n"
    )
    _bump_version_to(monkeypatch, "0.99.0")
    _write_template_for(monkeypatch, "AGENTS.md", new_template)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0, result.output

    after = agents_path.read_text(encoding="utf-8")
    assert "Brand new managed content" in after
    assert "My personal additions" in after
    assert "Do the thing my way." in after
