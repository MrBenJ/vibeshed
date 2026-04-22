"""Tests for how ``vibeshed run`` picks a Python interpreter."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from vibeshed.cli import app
from vibeshed.commands._common import (
    VENV_PYTHON_ENV,
    project_venv_python,
    resolve_python_interpreter,
)


def test_resolver_prefers_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(VENV_PYTHON_ENV, "/tmp/custom-python")
    assert resolve_python_interpreter(tmp_path) == "/tmp/custom-python"


def test_resolver_prefers_project_venv_over_sys_executable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(VENV_PYTHON_ENV, raising=False)
    venv_python = _make_fake_venv_python(tmp_path)

    assert resolve_python_interpreter(tmp_path) == str(venv_python)


def test_resolver_env_override_wins_over_project_venv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_fake_venv_python(tmp_path)
    monkeypatch.setenv(VENV_PYTHON_ENV, "/tmp/custom-python")
    assert resolve_python_interpreter(tmp_path) == "/tmp/custom-python"


def test_resolver_falls_back_to_sys_executable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(VENV_PYTHON_ENV, raising=False)
    assert project_venv_python(tmp_path) is None
    assert resolve_python_interpreter(tmp_path) == sys.executable


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX shim script")
def test_run_uses_project_venv_python(
    initialized_project: Path,
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end: ``vibeshed run`` routes through ``.venv/bin/python`` when present."""
    monkeypatch.delenv(VENV_PYTHON_ENV, raising=False)
    shim = _install_venv_shim(initialized_project, marker="[via venv python]")

    runner.invoke(app, ["new", "venv-job"])
    main_script = initialized_project / "jobs" / "venv-job" / "scripts" / "main.py"
    main_script.write_text("print('main ran')\n", encoding="utf-8")

    result = runner.invoke(app, ["run", "venv-job"])
    assert result.exit_code == 0, result.output

    runs = json.loads(
        (initialized_project / "logs" / "venv-job" / "runs.json").read_text()
    )
    assert next(iter(runs["runs"].values()))["status"] == "SUCCESS"

    log_files = list((initialized_project / "logs" / "venv-job").rglob("run_*.log"))
    log_text = log_files[0].read_text()
    assert "[via venv python]" in log_text, (
        f"expected shim marker in log, got: {log_text!r}"
    )
    assert "main ran" in log_text
    assert shim.exists()  # sanity: the shim wasn't cleaned up mid-run


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX shim script")
def test_env_override_beats_project_venv_in_run(
    initialized_project: Path,
    runner: CliRunner,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``VIBESHED_PYTHON`` wins over ``.venv/bin/python`` even when both exist."""
    _install_venv_shim(initialized_project, marker="[via venv python]")

    override_dir = tmp_path_factory.mktemp("override")
    override = override_dir / "override-python"
    override.write_text(
        "#!/bin/sh\n"
        'echo "[via VIBESHED_PYTHON]"\n'
        f'exec {sys.executable} "$@"\n',
        encoding="utf-8",
    )
    override.chmod(override.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv(VENV_PYTHON_ENV, str(override))

    runner.invoke(app, ["new", "override-job"])
    main_script = (
        initialized_project / "jobs" / "override-job" / "scripts" / "main.py"
    )
    main_script.write_text("print('main ran')\n", encoding="utf-8")

    result = runner.invoke(app, ["run", "override-job"])
    assert result.exit_code == 0, result.output

    log_files = list((initialized_project / "logs" / "override-job").rglob("run_*.log"))
    log_text = log_files[0].read_text()
    assert "[via VIBESHED_PYTHON]" in log_text
    assert "[via venv python]" not in log_text


def test_doctor_warns_when_requirements_exist_without_venv(
    initialized_project: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(VENV_PYTHON_ENV, raising=False)
    assert (initialized_project / "requirements.txt").exists()
    assert project_venv_python(initialized_project) is None

    result = runner.invoke(app, ["doctor"])
    # doctor exits 0 for warnings; only hard failures (missing git, etc.) non-zero.
    assert "requirements.txt exists but no .venv" in result.output
    assert "uv venv" in result.output


def test_doctor_reports_detected_venv(
    initialized_project: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(VENV_PYTHON_ENV, raising=False)
    _make_fake_venv_python(initialized_project)

    result = runner.invoke(app, ["doctor"])
    assert "Project .venv detected" in result.output
    assert "requirements.txt exists but no .venv" not in result.output


def _make_fake_venv_python(project_root: Path) -> Path:
    """Create a non-executable placeholder at the platform-appropriate venv path."""
    if sys.platform.startswith("win"):
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True, exist_ok=True)
    venv_python.write_text("", encoding="utf-8")
    return venv_python


def _install_venv_shim(project_root: Path, *, marker: str) -> Path:
    """Install a shell shim at ``.venv/bin/python`` that tags output with ``marker``."""
    shim = project_root / ".venv" / "bin" / "python"
    shim.parent.mkdir(parents=True, exist_ok=True)
    shim.write_text(
        "#!/bin/sh\n"
        f'echo "{marker}"\n'
        f'exec {sys.executable} "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return shim
