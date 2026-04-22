# Agent Install Instructions for VibeShed

**Audience:** an AI coding agent (Claude Code, Cursor, etc.) that a user has asked to install VibeShed.

Follow these steps in order. Prompt the user at each decision point — do not silently pick paths for them.

## 1. Confirm prerequisites

Run these checks and report any missing tool to the user before continuing:

```sh
python3 --version   # need >= 3.9
pipx --version      # preferred installer; if missing, fall back to: pip install --user vibeshed
uv --version        # optional, only for faster venv + deps install
git --version       # needed if you install the Claude Code plugin from a git clone
```

If `python3` is < 3.9 or missing, stop and tell the user — VibeShed requires Python 3.9+.

## 2. Install the CLI

```sh
pipx install vibeshed
```

Fallback without `pipx`:

```sh
python3 -m pip install --user vibeshed
```

Verify:

```sh
vibeshed --help
```

## 3. Ask the user where the VibeShed project should live

Ask, do not guess. A sensible default to offer: `~/vibeshed-projects/default`. Let the user override.

Once they pick a path, call it `$PROJECT_PATH` from here on.

## 4. Scaffold the project

```sh
vibeshed init "$PROJECT_PATH"
cd "$PROJECT_PATH"
```

This creates `registry.yaml`, `jobs/`, `shared/`, `AGENTS.md`, `CLAUDE.md`, `PRINCIPLES.md`, and `.vibeshed/manifest.json`.

## 5. Create the project virtual environment

`vibeshed run` spawns scripts with `$PROJECT_PATH/.venv/bin/python` when it exists, so jobs see the deps listed in `requirements.txt`. Create it:

```sh
# Preferred:
uv venv && uv pip install -r requirements.txt
# Fallback:
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Verify the interpreter VibeShed will actually use:

```sh
vibeshed doctor
```

If `doctor` warns about a missing `.venv`, go back and fix it before moving on.

## 6. Install the Claude Code plugin

This gives the user `/vibeshed:run` and `/vibeshed:set-project` inside Claude Code.

**Option A — local clone of this repo:**

```sh
# If the vibeshed source repo isn't already checked out somewhere:
git clone https://github.com/vibeshed/vibeshed.git ~/src/vibeshed
```

Then, inside Claude Code, ask the user to run:

```
/plugin install ~/src/vibeshed/plugin
```

(Adjust the path to wherever they cloned.)

**Option B — point at an existing checkout:**

If the user already has this repo checked out, tell them the absolute path to the `plugin/` directory and have them run `/plugin install <that-path>` in Claude Code.

After install, confirm both commands appear:

```
/vibeshed:set-project
/vibeshed:run
```

## 7. Point the plugin at the project

Inside Claude Code, have the user run:

```
/vibeshed:set-project <absolute-path-to-project>
```

This writes `~/.config/vibeshed/project` so `/vibeshed:run` works from any working directory.

The env var `VIBESHED_PROJECT` overrides the config file if the user wants a per-shell override.

## 8. Create a first job and verify the loop

```sh
cd "$PROJECT_PATH"
vibeshed new hello
```

Edit `jobs/hello/scripts/main.py` and `jobs/hello/sequence.md` with the user. Then validate and run:

```sh
vibeshed validate
vibeshed run hello
```

Or, from Claude Code anywhere on the system:

```
/vibeshed:run hello
```

Confirm `logs/hello/runs.json` records a SUCCESS entry.

## 9. Hand off

Tell the user:

- Jobs live in `$PROJECT_PATH/jobs/<slug>/`.
- Framework files (`shared/`, `CLAUDE.md`, etc.) are tracked in `.vibeshed/manifest.json` — use `vibeshed update` to pull framework updates with three-way merge.
- `registry.yaml`, `jobs/`, `state/`, `logs/`, and `.env` are 100% theirs.
- Read `$PROJECT_PATH/PRINCIPLES.md` for the four rules every job follows.

## Troubleshooting checklist

Run in order if anything is off:

1. `vibeshed --version` — is the CLI installed and new enough?
2. `vibeshed doctor` (inside `$PROJECT_PATH`) — any red flags?
3. `vibeshed validate` — is the registry and job structure consistent?
4. `cat ~/.config/vibeshed/project` — is the plugin pointed at the right project?
5. `echo $VIBESHED_PROJECT` — is an env var overriding the config file unexpectedly?
