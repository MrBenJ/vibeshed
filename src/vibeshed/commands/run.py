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

from vibeshed.commands._common import find_project_root, load_registry


def run(
    slug: str = typer.Argument(..., help="Slug of the job to run."),
    trigger: str = typer.Option(
        "cli",
        "--trigger",
        help="What triggered this run. Recorded in runs.json. Common values: cli, cron, manual, agent.",
    ),
    agent_id: Optional[str] = typer.Option(
        None, "--agent-id", help="Agent type/platform identifier (e.g. claude-cowork)."
    ),
    agent_instance: Optional[str] = typer.Option(
        None, "--agent-instance", help="Specific agent session/instance identifier."
    ),
) -> None:
    """Execute jobs/<slug>/scripts/main.py and record the result."""
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
    start = time.monotonic()
    with log_file.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            [sys.executable, str(main_script)],
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        fh.write(proc.stdout or "")
    duration_ms = int((time.monotonic() - start) * 1000)

    status = "SUCCESS" if proc.returncode == 0 else "FAILURE"
    error = None if proc.returncode == 0 else _last_lines(proc.stdout or "", 5)

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

    if proc.stdout:
        typer.echo(proc.stdout, nl=False)

    raise typer.Exit(code=0 if status == "SUCCESS" else 1)


def _load_runs(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"runs": {}}


def _save_runs(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _last_lines(text: str, n: int) -> str:
    return "\n".join(text.splitlines()[-n:]) if text else ""
