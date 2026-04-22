# VibeShed Claude Code Plugin

Slash commands for running [VibeShed](https://github.com/vibeshed/vibeshed) jobs from Claude Code.

## Commands

| Command | Purpose |
| --- | --- |
| `/vibeshed:set-project <abs-path>` | Record which VibeShed project to target. |
| `/vibeshed:run <slug> [-- --key value ...]` | Run a job by slug, forwarding passthrough args. |

## Install

From inside Claude Code, with this repo checked out locally:

```
/plugin install /absolute/path/to/vibeshed/plugin
```

Or reference the git repo if your Claude Code build supports it.

## Project resolution

`/vibeshed:run` picks a project in this order:

1. `$VIBESHED_PROJECT` (env var).
2. `~/.config/vibeshed/project` (written by `/vibeshed:set-project`).
3. The current working directory, if it has `registry.yaml` and `.vibeshed/manifest.json`.

## Prerequisites

- `vibeshed` CLI on `PATH` (`pipx install vibeshed`).
- A scaffolded project (`vibeshed init <path>`).

See [`AGENTS_INSTALL_INSTRUCTIONS.md`](../AGENTS_INSTALL_INSTRUCTIONS.md) in the repo root for the full install walkthrough — intended to be read and executed by an agent.
