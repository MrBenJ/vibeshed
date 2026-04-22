<!-- vibeshed:managed:start v0.1.1 -->
# Agent Guidelines for VibeShed

Conventions any agent should follow when working in a VibeShed repo. The canonical rules for vibeshed-style automations live in [`PRINCIPLES.md`](PRINCIPLES.md) — read that first.

## Core Principles (summary)

1. **Scripts are simple and composable** — small python scripts, shared helpers in `shared/`.
2. **Params pass through the CLI** — `vibeshed run <slug> -- --key value` forwards everything after `--` to the script.
3. **Success or failure, nothing in between** — exit `0` on success, non-zero on failure. `runs.json` is the source of truth.
4. **Errors have a timeout** — `config.yaml`'s `timeout_minutes` is enforced by `vibeshed run`.

See `PRINCIPLES.md` for full detail and examples.

## Job Structure

- Each job lives in `jobs/{slug}/`.
- `sequence.md` documents **Inputs → Action → Result** (what the job accepts, what it does, what it emits).
- `config.yaml` holds job settings (`timeout_minutes`, any custom knobs).
- `scripts/` contains the deterministic scripts.
- Never modify files outside the job folder, except `shared/` and `state/`.

## Creating a New Job

Prefer the CLI over hand-editing:

```sh
vibeshed new <slug>
```

Then:

1. Update the entry in `registry.yaml` with the real description, tags, and dependencies.
2. Edit `jobs/{slug}/sequence.md` with the Inputs, Action, and Result sections.
3. Implement `jobs/{slug}/scripts/main.py` — parse `argparse` args for any params, exit `0`/non-zero.
4. Run `vibeshed validate` to check the structure.
5. Test with `vibeshed run <slug> -- <params>`.

## Running Jobs

Always use the CLI rather than invoking scripts directly:

```sh
vibeshed run <slug> -- --param1 value --param2 value
```

Everything after `--` is forwarded verbatim to `scripts/main.py`. The CLI sets `JOB_SLUG`, captures logs, enforces `timeout_minutes`, and records the outcome in `logs/<slug>/runs.json`. If you must run a single step manually, set `JOB_SLUG=<slug>` so logging routes correctly.

### Project interpreter

Jobs are spawned with `<project>/.venv/bin/python` when that file exists (so scripts see the deps listed in `requirements.txt`), otherwise with the CLI's own interpreter. On a new checkout, run:

```sh
uv venv && uv pip install -r requirements.txt
```

Set `VIBESHED_PYTHON` to override. `vibeshed doctor` surfaces the effective interpreter and warns when `requirements.txt` is present but `.venv` is not.

## Environment Variables

- Check `dependencies.env_vars` in `registry.yaml` before running a job.
- If an env var is missing, log a clear error and fail fast.
- Never hardcode secrets in scripts. Read from `os.getenv` or `.env`.

## Shared Utilities

Import from the `shared` package:

```python
from shared import logging, state, notifications, api_clients
```

Extend shared utilities for common patterns; don't duplicate. Keep shared code generic — job-specific logic belongs in the job folder.

## Logging

- Use `logging.get_logger(__name__)` — never `print()`.
- INFO for normal operations, ERROR with `exc_info=True` for failures.

## State

- Use `StateManager(job_slug)` for persistence across runs.
- Store timestamps in ISO 8601 format.
- Keep state files under ~1MB.

## Error Handling

- Catch exceptions at the job level and log full tracebacks.
- Send error notifications for failures.
- Exit non-zero on failure.
- Do not leave jobs in partially-completed states.
- Set `timeout_minutes` in `config.yaml` to 2–3× expected runtime so flakes fail loudly.
<!-- vibeshed:managed:end -->

<!-- Add your project-specific agent conventions below this line. They will be preserved across `vibeshed update`. -->
