# VibeShed

A lightweight, agent-agnostic framework for building personal automations.

VibeShed is for **vibe-coding automations** with an agent in the loop. Every job is a folder of plain files (`config.yaml`, `sequence.md`, `scripts/main.py`) that an agent can read, modify, and call. The `vibeshed` CLI runs those jobs so cron, CI, another agent, or a human can invoke them with the same interface.

## Install

```sh
pipx install vibeshed
```

## Quickstart

```sh
vibeshed init my-automations
cd my-automations
uv venv && uv pip install -r requirements.txt   # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
vibeshed new daily-briefing
# edit jobs/daily-briefing/scripts/main.py
vibeshed run daily-briefing -- --date 2026-04-19
vibeshed logs daily-briefing
```

Everything after `--` is forwarded to `scripts/main.py`. Parse params with `argparse` (the template scaffolds this for you).

### Project interpreter

`vibeshed run` spawns `scripts/main.py` with the project's own Python so jobs see the deps in `requirements.txt`. Resolution order:

1. `$VIBESHED_PYTHON` if set — explicit escape hatch for pinned interpreters.
2. `<project>/.venv/bin/python` if it exists — the default, created by the `uv venv` step above.
3. The interpreter running the CLI (e.g. the `pipx` env) — fallback for projects with no deps.

Run `vibeshed doctor` to see which interpreter will be used and get warned when `requirements.txt` has no matching `.venv`.

## What it means to be one with the vibeshed

Every job follows four rules. The long form lives in [`PRINCIPLES.md`](src/vibeshed/templates/PRINCIPLES.md) — scaffolded into every project at `PRINCIPLES.md`.

1. **Scripts are simple and composable** — small python scripts that lean on `shared/` for logging, state, notifications, and API clients.
2. **Params pass through the CLI** — `vibeshed run <slug> -- --key value` forwards everything after `--` to the script. No magic wrapper layer.
3. **Success or failure, nothing in between** — scripts exit `0` on success, non-zero on failure. `logs/<slug>/runs.json` records the outcome.
4. **Errors have a timeout** — `config.yaml`'s `timeout_minutes` is enforced by `vibeshed run`; hitting it is a FAILURE with `error: "timeout ..."`.

Agents working in a VibeShed repo use these principles to guide users through vibe-coding new automations.

## Commands

| Command | Purpose |
| --- | --- |
| `vibeshed init [path]` | Scaffold a new automations repo. |
| `vibeshed new <slug>` | Create a new job from the template. |
| `vibeshed run <slug> -- <params>` | Execute a job's `scripts/main.py` with passthrough args, enforce `timeout_minutes`, record the run. |
| `vibeshed list` | List all registered jobs. |
| `vibeshed validate` | Lint `registry.yaml` and job folder structure. |
| `vibeshed status` | Show framework version and any drift in managed files. |
| `vibeshed update [--dry-run]` | Pull the latest framework files with three-way merge. |
| `vibeshed logs <slug> [-n N]` | Tail recent logs for a job. |
| `vibeshed doctor` | Check environment, dependencies, and structure. |
| `vibeshed eject` | Stop tracking framework files — full ownership, no more updates. |

## How updates work

Files like `shared/`, `AGENTS.md`, `CLAUDE.md`, and `PRINCIPLES.md` are **framework-managed**. VibeShed records their original SHAs in `.vibeshed/manifest.json` so `vibeshed update` can:

- Cleanly overwrite files you haven't touched.
- Preserve files where only you changed them.
- Three-way merge files that both you and the framework changed (delegated to `git merge-file`).
- Preserve any content you add **outside** the `<!-- vibeshed:managed:start -->` / `<!-- vibeshed:managed:end -->` markers in `AGENTS.md`, `CLAUDE.md`, `PRINCIPLES.md`, `.gitignore`, and `requirements.txt`.

`registry.yaml`, `jobs/`, `state/`, `logs/`, and `.env` are never touched by `update`. They are 100% yours.

If you outgrow the framework, `vibeshed eject` strips the markers and the manifest so you can take full ownership without forking.

## License

MIT
