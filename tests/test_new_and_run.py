"""Tests for ``vibeshed new`` and ``vibeshed run``."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from vibeshed.cli import app


def test_new_scaffolds_and_registers_job(initialized_project: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["new", "hello-world", "--name", "Hello World"])
    assert result.exit_code == 0, result.output

    job_dir = initialized_project / "jobs" / "hello-world"
    assert (job_dir / "config.yaml").exists()
    assert (job_dir / "sequence.md").exists()
    assert (job_dir / "scripts" / "main.py").exists()

    main_text = (job_dir / "scripts" / "main.py").read_text()
    assert "hello-world" in main_text  # slug substitution worked

    registry_text = (initialized_project / "registry.yaml").read_text()
    assert "hello-world:" in registry_text


def test_new_rejects_invalid_slug(initialized_project: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["new", "BadSlug"])
    assert result.exit_code != 0
    assert "kebab-case" in result.output.lower() or "invalid slug" in result.output.lower()


def test_run_executes_main_and_records(initialized_project: Path, runner: CliRunner) -> None:
    runner.invoke(app, ["new", "echo-job"])
    main_script = initialized_project / "jobs" / "echo-job" / "scripts" / "main.py"
    main_script.write_text(
        "import sys\nprint('hello from main')\nsys.exit(0)\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["run", "echo-job"])
    assert result.exit_code == 0, result.output

    runs = json.loads((initialized_project / "logs" / "echo-job" / "runs.json").read_text())
    assert len(runs["runs"]) == 1
    entry = next(iter(runs["runs"].values()))
    assert entry["status"] == "SUCCESS"
    assert entry["trigger"] == "cli"
    assert entry["duration_ms"] >= 0

    log_files = list((initialized_project / "logs" / "echo-job").rglob("run_*.log"))
    assert len(log_files) == 1
    assert "hello from main" in log_files[0].read_text()


def test_run_records_failure(initialized_project: Path, runner: CliRunner) -> None:
    runner.invoke(app, ["new", "fail-job"])
    main_script = initialized_project / "jobs" / "fail-job" / "scripts" / "main.py"
    main_script.write_text("import sys\nsys.exit(2)\n", encoding="utf-8")

    result = runner.invoke(app, ["run", "fail-job"])
    assert result.exit_code != 0

    runs = json.loads((initialized_project / "logs" / "fail-job" / "runs.json").read_text())
    entry = next(iter(runs["runs"].values()))
    assert entry["status"] == "FAILURE"


def test_run_unknown_slug(initialized_project: Path, runner: CliRunner) -> None:
    result = runner.invoke(app, ["run", "nope"])
    assert result.exit_code != 0
    assert "not registered" in result.output.lower()


def test_run_forwards_passthrough_args(
    initialized_project: Path, runner: CliRunner
) -> None:
    runner.invoke(app, ["new", "echo-args"])
    main_script = initialized_project / "jobs" / "echo-args" / "scripts" / "main.py"
    main_script.write_text(
        "import sys\nprint('argv:' + '|'.join(sys.argv[1:]))\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app, ["run", "echo-args", "--", "--name", "ben", "--flag"]
    )
    assert result.exit_code == 0, result.output

    log_files = list((initialized_project / "logs" / "echo-args").rglob("run_*.log"))
    assert len(log_files) == 1
    assert "argv:--name|ben|--flag" in log_files[0].read_text()


def test_run_enforces_config_timeout(
    initialized_project: Path, runner: CliRunner
) -> None:
    runner.invoke(app, ["new", "slow-job"])
    config_path = initialized_project / "jobs" / "slow-job" / "config.yaml"
    config_path.write_text("timeout_minutes: 0.02\n", encoding="utf-8")  # 1.2s
    main_script = initialized_project / "jobs" / "slow-job" / "scripts" / "main.py"
    main_script.write_text(
        "import time\nprint('starting')\ntime.sleep(10)\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["run", "slow-job"])
    assert result.exit_code != 0

    runs = json.loads(
        (initialized_project / "logs" / "slow-job" / "runs.json").read_text()
    )
    entry = next(iter(runs["runs"].values()))
    assert entry["status"] == "FAILURE"
    assert "timeout" in (entry["error"] or "").lower()
