<!-- vibeshed:managed:start v0.1.1 -->
# VibeShed Principles

What it means to **be one with the vibeshed**. These are the rules every job follows so agents and humans can mix and match them without surprises.

## 1. Scripts are simple and composable

Every job is a small python script (or a handful of them) that does one useful thing and leans on `shared/` for the boring parts — logging, state, notifications, API clients. If two jobs need the same helper, the helper belongs in `shared/`, not copy-pasted.

```python
from shared import logging, state, notifications
```

## 2. Params pass through the CLI

Anything after `--` on the `vibeshed run` command is forwarded verbatim to `scripts/main.py`. Jobs parse their own args with `argparse` (or whatever they prefer) — there is no magic wrapper layer.

```sh
vibeshed run daily-briefing -- --date 2026-04-19 --user ben
```

Document the params a job expects in `sequence.md`'s **Inputs** section so agents can invoke it correctly.

## 3. Success or failure, nothing in between

Scripts exit `0` on success and non-zero on failure. `vibeshed run` records the outcome in `logs/<slug>/runs.json` along with duration, log path, and the last lines of output on failure. No "partial" states — if a step fails, the whole run fails.

## 4. Errors have a timeout

Every job has a `timeout_minutes` in its `config.yaml`. `vibeshed run` kills the process and records a FAILURE with `error: "timeout ..."` if it runs long. Pick a timeout that's roughly 2–3× your expected runtime so flakes fail loudly instead of hanging silently.

```yaml
# jobs/<slug>/config.yaml
timeout_minutes: 5
```

---

Agents guiding a user through vibe-coding a new automation should enforce these four principles. If a proposed job doesn't fit them, that's usually a sign the job should be split, or a helper should move into `shared/`.
<!-- vibeshed:managed:end -->

<!-- Add your project-specific principles below this line. They will be preserved across `vibeshed update`. -->
