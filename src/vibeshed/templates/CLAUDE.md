<!-- vibeshed:managed:start v0.1.1 -->
# Claude Code Instructions for VibeShed

You help users run existing automations and vibe-code new ones that follow the [vibeshed principles](PRINCIPLES.md): simple composable scripts, CLI passthrough params, success/failure exit codes, and enforced timeouts. Prefer the `vibeshed` CLI over raw shell whenever it's available — every command below has been designed to give you a structured, predictable interface.

## First-time setup

`vibeshed run` spawns `scripts/main.py` with the project's own Python so jobs can `import requests`, `yaml`, and anything else in `requirements.txt`. On a fresh clone, create the project `.venv` before running any job:

```sh
uv venv && uv pip install -r requirements.txt
# or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

If `.venv/bin/python` is missing, the CLI falls back to whichever interpreter it's installed under (often the `pipx` env), which typically does not have the project deps. `vibeshed doctor` warns in that case. To pin a different interpreter, set `VIBESHED_PYTHON=/abs/path/to/python`.

## Quick Reference

| Intent | Command |
| --- | --- |
| List all jobs | `vibeshed list` |
| Run a job | `vibeshed run <slug> -- <params>` |
| Create a new job | `vibeshed new <slug>` |
| Validate the repo | `vibeshed validate` |
| Check recent logs | `vibeshed logs <slug> -n 50` |
| Check framework health | `vibeshed doctor` |
| Check framework version / drift | `vibeshed status` |
| Pull framework updates | `vibeshed update` |

## Commands

### Run a Job

When the user says "run {slug}":

1. Confirm the job exists with `vibeshed list`.
2. Read `jobs/{slug}/sequence.md` — the **Inputs** section lists the params the script expects and any required env vars.
3. Check `dependencies.env_vars` in `registry.yaml` — ask the user for any missing values.
4. Run with `vibeshed run <slug> -- <params>`. Everything after `--` is forwarded to `scripts/main.py`.
5. If it fails, show the recent logs with `vibeshed logs <slug>`.

### Create a New Job

When the user says "create job {name}":

1. Generate a kebab-case slug from the name.
2. Run `vibeshed new <slug>` to scaffold the folder.
3. Ask for: description, expected params (name, type, required?), required env vars, what each step does, what result/notification they want.
4. Update the entry in `registry.yaml` with the real description, tags, and `dependencies`.
5. Fill in `jobs/{slug}/sequence.md` with the Inputs, Action, and Result sections.
6. Implement `jobs/{slug}/scripts/main.py`:
   - Parse params with `argparse`.
   - Exit `0` on success, non-zero on failure.
   - Use `from shared import logging` — never `print()`.
   - For multi-step jobs, split into scripts under `scripts/` and reference them in `sequence.md`.
7. Set a realistic `timeout_minutes` in `jobs/{slug}/config.yaml` (2–3× expected runtime).
8. Run `vibeshed validate` to check the structure.
9. Test with `vibeshed run <slug> -- <params>`.

### Multi-Step Orchestration

If `sequence.md` has multiple step scripts and you need to chain them with conditional logic:

- Run each step directly: `JOB_SLUG=<slug> python jobs/<slug>/scripts/<step>.py <args>`
- Pipe stdin/stdout between steps as documented in `sequence.md`.
- Decide whether to skip steps based on previous outputs.

If the job is a single straight-through pipeline, prefer `vibeshed run <slug> -- <params>` — it executes `scripts/main.py`, enforces the timeout, and records the run.

## Code Style

- Use type hints on function signatures.
- Document functions with docstrings.
- Handle errors gracefully with try/except at the job level.
- Use `from shared import logging` — never the stdlib `logging` directly, never `print()`.
- Parse params with `argparse` so `vibeshed run <slug> -- --foo bar` works.

## sequence.md Skeleton

```markdown
# Job: {Name}

[Brief description.]

## Inputs

- Params (passed after `--` on `vibeshed run`):
  - `--date` (required) — ISO date, e.g. `2026-04-19`.
  - `--user` (optional) — target user slug.
- Env vars:
  - `SOME_API_KEY` — required.

## Action

### Step 1: [Description]
Run: `scripts/{script_name}.py`
- Input: [params / env / stdin / files]
- Output: [JSON / text / files]

## Result

### On Success
- [State updates, notifications.]

### On Failure
- [Retry, alert, cleanup.]

## Notes
[Edge cases, special considerations, timeout reasoning.]
```

## Testing a New Job

Before declaring a job complete:

1. `vibeshed run <slug> -- <params>` — verify it succeeds.
2. `vibeshed logs <slug>` — verify the log file was created.
3. Inspect `logs/<slug>/runs.json` — confirm a SUCCESS entry exists.
4. Check that state was updated (if applicable).
5. Confirm notifications were sent (if configured).
6. Verify timeout behavior: set a tight `timeout_minutes`, force a slow run, and confirm FAILURE is recorded with `error` mentioning `timeout`.
<!-- vibeshed:managed:end -->

<!-- Add your project-specific Claude Code instructions below this line. They will be preserved across `vibeshed update`. -->
