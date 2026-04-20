"""Tests for ``vibeshed init``."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from vibeshed.cli import app
from vibeshed.templates_loader import INIT_DIRECTORIES, MANAGED_FILES, UNMANAGED_INIT_FILES


def test_init_creates_full_structure(tmp_path: Path, runner: CliRunner) -> None:
    project = tmp_path / "demo"
    result = runner.invoke(app, ["init", str(project)])
    assert result.exit_code == 0, result.output

    for rel in (*MANAGED_FILES, *UNMANAGED_INIT_FILES):
        assert (project / rel).exists(), f"missing template file: {rel}"

    for directory in INIT_DIRECTORIES:
        assert (project / directory).is_dir(), f"missing directory: {directory}"

    manifest_path = project / ".vibeshed" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["framework_version"]
    for rel in MANAGED_FILES:
        assert rel in manifest["files"]
        assert manifest["files"][rel]["sha"]
        assert manifest["files"][rel]["mode"] in {"full", "marker"}

    for rel in MANAGED_FILES:
        assert (project / ".vibeshed" / "cache" / rel).exists(), f"missing cache: {rel}"


def test_init_refuses_to_overwrite_existing_project(
    tmp_path: Path, runner: CliRunner
) -> None:
    project = tmp_path / "demo"
    runner.invoke(app, ["init", str(project)])
    result = runner.invoke(app, ["init", str(project)])
    assert result.exit_code != 0
    assert "already exists" in result.output.lower()
