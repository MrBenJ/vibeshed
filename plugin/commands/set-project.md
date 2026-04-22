---
description: Point /vibeshed:run at a specific VibeShed project directory.
argument-hint: "<absolute-path-to-vibeshed-project>"
allowed-tools: ["Bash"]
---

# /vibeshed:set-project

Record the absolute path of a VibeShed project so `/vibeshed:run` can target it from anywhere.

**Argument:** `$ARGUMENTS`

## Steps

1. **Resolve to an absolute path.** If `$ARGUMENTS` is empty, stop and ask the user for the path. Expand `~` via the shell. Example:
   ```bash
   PROJECT_PATH="$(cd "$ARGUMENTS" 2>/dev/null && pwd)"
   ```
   If `PROJECT_PATH` is empty, the directory does not exist — stop and tell the user.

2. **Verify it is a VibeShed project.** Both files must exist:
   - `$PROJECT_PATH/registry.yaml`
   - `$PROJECT_PATH/.vibeshed/manifest.json`

   If either is missing, stop and tell the user:
   > `$PROJECT_PATH` does not look like a VibeShed project. Run `vibeshed init <path>` there first.

3. **Persist the path.**
   ```bash
   mkdir -p ~/.config/vibeshed
   printf '%s\n' "$PROJECT_PATH" > ~/.config/vibeshed/project
   ```

4. **Confirm and list.** Run `cd "$PROJECT_PATH" && vibeshed list` to show the user which jobs are now reachable via `/vibeshed:run`.

## Notes

- `VIBESHED_PROJECT` in the environment takes precedence over this config file — mention that if the user seems to be hitting a different project than they expect.
