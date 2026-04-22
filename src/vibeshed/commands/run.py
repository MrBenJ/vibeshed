"""``vibeshed run`` — execute a job's ``scripts/main.py`` deterministically."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
import yaml

from vibeshed.commands._common import find_project_root, load_registry

DEFAULT_TIMEOUT_MINUTES = 5.0


def run(
    ctx: typer.Context,
    slug: str = typer.Argument(..., help="Slug of the job to run."),
    trigger: str = typer.Option(
        "cli",
        "--trigger",
        help="What invoked this run. Recorded in runs.json. Common values: cli, cron, manual, agent.",
    ),
    agent_id: Optional[str] = typer.Option(
        None, "--agent-id", help="Agent type/platform identifier (e.g. claude-cowork)."
    ),
    agent_instance: Optional[str] = typer.Option(
        None, "--agent-instance", help="Specific agent session/instance identifier."
    ),
) -> None:
    """Execute ``jobs/<slug>/scripts/main.py`` and record the result.

    Any arguments after ``--`` on the command line are forwarded verbatim to
    the script, e.g. ``vibeshed run my-job -- --date 2026-04-19 --user ben``.
    """
    project_root = find_project_root()
    registry = load_registry(project_root)
    if slug not in registry["jobs"]:
        typer.secho(
            f"Job {slug!r} is not registered. Run `vibeshed list` to see jobs, "
            f"or `vibeshed new {slug}` to create it.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    main_script = project_root / "jobs" / slug / "scripts" / "main.py"
    if not main_script.exists():
        typer.secho(
            f"No main.py found at {main_script}. The CLI runs scripts/main.py strictly.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    timeout_minutes = _read_timeout_minutes(project_root / "jobs" / slug / "config.yaml")
    timeout_seconds = timeout_minutes * 60

    passthrough_args = list(ctx.args)

    started = datetime.now()
    timestamp_iso = started.replace(microsecond=0).isoformat()
    log_dir = project_root / "logs" / slug / started.strftime("%Y-%m-%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"run_{started.strftime('%H-%M-%S')}"
    log_file = log_dir / f"{run_id}.log"

    env = os.environ.copy()
    env["JOB_SLUG"] = slug
    env["PYTHONPATH"] = str(project_root) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )

    typer.secho(f"▶ {slug} ({run_id})", fg=typer.colors.CYAN)
    cmd = [sys.executable, str(main_script), *passthrough_args]
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
        )
        stdout = proc.stdout or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as te:
        timed_out = True
        stdout = (te.stdout or "") if isinstance(te.stdout, str) else ""
        returncode = -1
    duration_ms = int((time.monotonic() - start) * 1000)

    log_file.write_text(stdout, encoding="utf-8")

    if timed_out:
        status = "FAILURE"
        error = f"timeout after {timeout_minutes} minutes"
    elif returncode == 0:
        status = "SUCCESS"
        error = None
    else:
        status = "FAILURE"
        error = _last_lines(stdout, 5)

    runs_file = project_root / "logs" / slug / "runs.json"
    runs = _load_runs(runs_file)
    runs["runs"][timestamp_iso] = {
        "run_id": run_id,
        "status": status,
        "duration_ms": duration_ms,
        "error": error,
        "agent_id": agent_id,
        "agent_instance": agent_instance,
        "trigger": trigger,
    }
    _save_runs(runs_file, runs)

    color = typer.colors.GREEN if status == "SUCCESS" else typer.colors.RED
    typer.secho(f"  {status} in {duration_ms}ms — {log_file}", fg=color)

    if stdout:
        typer.echo(stdout, nl=False)
    if timed_out:
        typer.secho(f"  (timeout: {timeout_minutes} minutes)", fg=typer.colors.RED, err=True)

    raise typer.Exit(code=0 if status == "SUCCESS" else 1)


def _read_timeout_minutes(config_path: Path) -> float:
    """Read ``timeout_minutes`` from a job's config.yaml. Falls back on 5.0."""
    if not config_path.exists():
        return DEFAULT_TIMEOUT_MINUTES
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return DEFAULT_TIMEOUT_MINUTES
    value = data.get("timeout_minutes", DEFAULT_TIMEOUT_MINUTES)
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_MINUTES
    return parsed if parsed > 0 else DEFAULT_TIMEOUT_MINUTES


def _load_runs(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"runs": {}}


def _save_runs(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _last_lines(text: str, n: int) -> str:
    return "\n".join(text.splitlines()[-n:]) if text else ""
