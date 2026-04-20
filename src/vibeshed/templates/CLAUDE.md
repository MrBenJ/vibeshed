<!-- vibeshed:managed:start v0.1.0 -->
# Claude Code Instructions for VibeShed

You help users run existing automations and build new ones following the **Trigger → Action → Result** framework. Prefer the `vibeshed` CLI over raw shell whenever it's available — every CLI command below has been designed to give you a structured, predictable interface.

## Quick Reference

| Intent | Command |
| --- | --- |
| List all jobs | `vibeshed list` |
| Run a job | `vibeshed run <slug>` |
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
2. Check `dependencies.env_vars` in `registry.yaml` — ask the user for any missing values.
3. Run with `vibeshed run <slug>`.
4. If it fails, show the recent logs with `vibeshed logs <slug>`.

### Create a New Job

When the user says "create job {name}":

1. Generate a kebab-case slug from the name.
2. Run `vibeshed new <slug>` to scaffold the folder.
3. Ask for: description, what each step does, expected inputs/outputs, what result/notification they want.
4. Update the entry in `registry.yaml` with the real description, tags, and `dependencies`.
5. Fill in `jobs/{slug}/sequence.md` with the Action and Result sections.
6. Implement `jobs/{slug}/scripts/main.py` (deterministic CLI entry point).
   - For multi-step jobs, also create one script per step under `scripts/` and reference them in `sequence.md`.
7. Run `vibeshed validate` to check the structure.
8. Test with `vibeshed run <slug>`.

### Multi-Step Orchestration

If `sequence.md` has multiple step scripts and you need to chain them with conditional logic:

- Run each step directly: `JOB_SLUG=<slug> python jobs/<slug>/scripts/<step>.py`
- Pipe stdin/stdout between steps as documented in `sequence.md`.
- Decide whether to skip steps based on previous outputs.

If the job is a single straight-through pipeline, prefer `vibeshed run <slug>` — it executes `scripts/main.py` and handles logging and run tracking for you.

## Code Style

- Use type hints on function signatures.
- Document functions with docstrings.
- Handle errors gracefully with try/except at the job level.
- Use `from shared import logging` — never the stdlib `logging` directly, never `print()`.

## sequence.md Skeleton

```markdown
# Job: {Name}

[Brief description.]

## Trigger
[Cron / on-demand / event / hybrid.]

## Action

### Step 1: [Description]
Run: `scripts/{script_name}.py`
- Input: [stdin / args / env / files]
- Output: [JSON / text / files]

## Result

### On Success
- [State updates, notifications.]

### On Failure
- [Retry, alert, cleanup.]

## Notes
[Edge cases, special considerations.]
```

## Testing a New Job

Before declaring a job complete:

1. `vibeshed run <slug>` — verify it succeeds.
2. `vibeshed logs <slug>` — verify the log file was created.
3. Inspect `logs/<slug>/runs.json` — confirm a SUCCESS entry exists.
4. Check that state was updated (if applicable).
5. Confirm notifications were sent (if configured).
<!-- vibeshed:managed:end -->

<!-- Add your project-specific Claude Code instructions below this line. They will be preserved across `vibeshed update`. -->
