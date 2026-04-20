"""Shared fixtures for VibeShed tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest
from typer.testing import CliRunner

from vibeshed.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def initialized_project(tmp_path: Path, runner: CliRunner) -> Iterator[Path]:
    """A scratch project that has had `vibeshed init` run inside it."""
    cwd = Path.cwd()
    project = tmp_path / "proj"
    result = runner.invoke(app, ["init", str(project)])
    assert result.exit_code == 0, result.output
    os.chdir(project)
    try:
        yield project
    finally:
        os.chdir(cwd)
