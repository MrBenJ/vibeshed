"""Tests for ``vibeshed eject``."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vibeshed.cli import app


def test_eject_strips_markers_and_removes_manifest(
    initialized_project: Path, runner: CliRunner
) -> None:
    agents = initialized_project / "AGENTS.md"
    assert "vibeshed:managed:start" in agents.read_text()

    result = runner.invoke(app, ["eject", "-y"])
    assert result.exit_code == 0, result.output

    assert "vibeshed:managed" not in agents.read_text()
    assert not (initialized_project / ".vibeshed").exists()
