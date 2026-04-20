# VibeShed

A lightweight, agent-agnostic framework for building personal automations.

Every automation in VibeShed is a **Trigger → Action → Result** flow, defined as a folder of plain files (`config.yaml`, `sequence.md`, `scripts/main.py`). Agents read those files to orchestrate work; the `vibeshed` CLI executes them so cron, CI, or any other trigger source can run jobs without an agent in the loop.

## Install

```sh
pipx install vibeshed
```

## Quickstart

```sh
vibeshed init my-automations
cd my-automations
vibeshed new daily-briefing
# edit jobs/daily-briefing/scripts/main.py
vibeshed run daily-briefing
vibeshed logs daily-briefing
```

## Commands

| Command | Purpose |
| --- | --- |
| `vibeshed init [path]` | Scaffold a new automations repo. |
| `vibeshed new <slug>` | Create a new job from the template. |
| `vibeshed run <slug>` | Execute a job's `scripts/main.py` and record the run. |
| `vibeshed list` | List all registered jobs. |
| `vibeshed validate` | Lint `registry.yaml` and job folder structure. |
| `vibeshed status` | Show framework version and any drift in managed files. |
| `vibeshed update [--dry-run]` | Pull the latest framework files with three-way merge. |
| `vibeshed logs <slug> [-n N]` | Tail recent logs for a job. |
| `vibeshed doctor` | Check environment, dependencies, and structure. |
| `vibeshed eject` | Stop tracking framework files — full ownership, no more updates. |

## How updates work

Files like `shared/`, `AGENTS.md`, and `CLAUDE.md` are **framework-managed**. VibeShed records their original SHAs in `.vibeshed/manifest.json` so `vibeshed update` can:

- Cleanly overwrite files you haven't touched.
- Preserve files where only you changed them.
- Three-way merge files that both you and the framework changed (delegated to `git merge-file`).
- Preserve any content you add **outside** the `<!-- vibeshed:managed:start -->` / `<!-- vibeshed:managed:end -->` markers in `AGENTS.md`, `CLAUDE.md`, `.gitignore`, and `requirements.txt`.

`registry.yaml`, `jobs/`, `state/`, `logs/`, and `.env` are never touched by `update`. They are 100% yours.

If you outgrow the framework, `vibeshed eject` strips the markers and the manifest so you can take full ownership without forking.

## License

MIT
