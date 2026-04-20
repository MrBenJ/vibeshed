"""Tests for ``vibeshed validate``."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vibeshed.cli import app


def test_validate_passes_after_init_and_new(
    initialized_project: Path, runner: CliRunner
) -> None:
    runner.invoke(app, ["new", "ok-job"])
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0, result.output
    assert "OK" in result.output


def test_validate_flags_missing_main_script(
    initialized_project: Path, runner: CliRunner
) -> None:
    runner.invoke(app, ["new", "broken-job"])
    (initialized_project / "jobs" / "broken-job" / "scripts" / "main.py").unlink()
    result = runner.invoke(app, ["validate"])
    assert result.exit_code != 0
    assert "main.py" in result.output


def test_validate_warns_on_orphan_folder(
    initialized_project: Path, runner: CliRunner
) -> None:
    runner.invoke(app, ["new", "registered"])
    orphan = initialized_project / "jobs" / "orphan"
    (orphan / "scripts").mkdir(parents=True)
    (orphan / "scripts" / "main.py").write_text("")
    (orphan / "config.yaml").write_text("")
    (orphan / "sequence.md").write_text("")
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "orphan" in result.output.lower()
