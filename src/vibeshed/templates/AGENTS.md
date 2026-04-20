<!-- vibeshed:managed:start v0.1.0 -->
# Agent Guidelines for VibeShed

Conventions any agent should follow when working in a VibeShed repo.

## Core Principles

1. **Trigger → Action → Result** — every automation defines all three.
2. **Fail safely** — errors are logged and notified, never swallowed.
3. **State is explicit** — use `shared/state.py`, not hidden globals.
4. **Logs are for humans** — write clear, readable messages.

## Job Structure

- Each job lives in `jobs/{slug}/`.
- `sequence.md` contains your action steps and result handling.
- `config.yaml` holds job settings (timeout, custom params).
- `scripts/` contains the deterministic scripts.
- Never modify files outside the job folder, except `shared/` and `state/`.

## Creating a New Job

Prefer the CLI over hand-editing:

```sh
vibeshed new <slug>
```

Then:

1. Update the entry in `registry.yaml` with the real description, tags, and dependencies.
2. Edit `jobs/{slug}/sequence.md` with the Action steps and Result handling.
3. Implement `jobs/{slug}/scripts/main.py` (or split into multiple step scripts).
4. Run `vibeshed validate` to check the structure.
5. Test with `vibeshed run <slug>`.

## Running Jobs

Always use the CLI rather than invoking scripts directly:

```sh
vibeshed run <slug>
```

This sets `JOB_SLUG`, captures logs to the right folder, and updates `runs.json`. If you must run a single step manually, set `JOB_SLUG=<slug>` so logging routes correctly.

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
<!-- vibeshed:managed:end -->

<!-- Add your project-specific agent conventions below this line. They will be preserved across `vibeshed update`. -->
