---
description: Run a VibeShed job by slug with passthrough params.
argument-hint: "<job-slug> [-- --param value ...]"
allowed-tools: ["Bash", "Read"]
---

# /vibeshed:run

Run the VibeShed job identified by the slug in `$ARGUMENTS`. This command targets the VibeShed project recorded by `/vibeshed:set-project` (or the `VIBESHED_PROJECT` env var, or — as a last resort — the current working directory if it is itself a VibeShed project).

**Arguments:** `$ARGUMENTS`

Parse `$ARGUMENTS` as `<slug> [extra args...]`. Everything after the slug is the passthrough argument list for `scripts/main.py`. If the user wrote a literal `--` separator, strip it — `vibeshed run` already inserts one.

## Resolve the project path

Try these in order and stop at the first one that exists and contains both `registry.yaml` and `.vibeshed/manifest.json`:

1. `$VIBESHED_PROJECT` environment variable.
2. The path stored in `~/.config/vibeshed/project` (single line, absolute path). Read it with:
   ```bash
   test -f ~/.config/vibeshed/project && cat ~/.config/vibeshed/project
   ```
3. The current working directory.

If none resolve, stop and tell the user:
> No VibeShed project configured. Run `/vibeshed:set-project <absolute-path>` first, or export `VIBESHED_PROJECT=<absolute-path>`.

From here on, refer to the resolved path as `$PROJECT`. Every `vibeshed` invocation below MUST run with `cwd=$PROJECT` — pass it via `cd "$PROJECT" && vibeshed ...` in a single Bash call.

## Steps

1. **Confirm the slug is registered.**
   ```bash
   cd "$PROJECT" && vibeshed list
   ```
   If the slug from `$ARGUMENTS` is not in the list, stop. Suggest `vibeshed new <slug>` to the user if they meant to create it.

2. **Read the job's contract.** Read `$PROJECT/jobs/<slug>/sequence.md` — the **Inputs** section lists expected params and env vars. Also read `$PROJECT/registry.yaml` and find the entry for `<slug>`; note any `dependencies.env_vars`.

3. **Check env vars.** For each var in `dependencies.env_vars`, run `printenv <VAR>` (in the resolved project shell). If any are unset, stop and ask the user to provide values before proceeding. Never hardcode secrets.

4. **Fill in missing params.** Compare the params the user supplied in `$ARGUMENTS` against the **Inputs** list in `sequence.md`. If any required params are missing, ask the user — one question per missing param.

5. **Run the job.**
   ```bash
   cd "$PROJECT" && vibeshed run <slug> --trigger agent --agent-id claude-code -- <passthrough-args>
   ```
   Forward everything the user supplied after the slug as `<passthrough-args>`. Do not wrap or interpret those args.

6. **Report the outcome.**
   - On exit 0: summarize the SUCCESS line and the log file path the CLI printed.
   - On non-zero exit: run `cd "$PROJECT" && vibeshed logs <slug> -n 50` and show the tail, then surface the error message from `runs.json`.

## Notes

- Do not run `scripts/main.py` directly. The CLI enforces `timeout_minutes` and records results in `logs/<slug>/runs.json`; bypassing it hides failures.
- Do not modify `registry.yaml`, `jobs/`, `state/`, or `logs/` while executing a run.
- If `vibeshed doctor` surfaces a `.venv` warning, tell the user but do not attempt to create the venv automatically — they may have a reason for the current interpreter choice.
