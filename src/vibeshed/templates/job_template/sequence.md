# Job: {{JOB_NAME}}

[Briefly describe what this job does.]

## Inputs

- Params (passed after `--` on `vibeshed run {{JOB_SLUG}}`):
  - `--example` (required) — [describe each param: type, purpose, example value].
- Env vars:
  - `EXAMPLE_API_KEY` — [describe; delete this block if none].

## Action

### Step 1: [Description]
Run: `scripts/main.py`
- Input: [params / stdin / env / files]
- Output: [What it produces]

[Add more steps as needed. Each step references one script.]

## Result

### On Success
- [State updates, notifications, side effects.]

### On Failure
- [Error notification, retry behavior, cleanup.]

## Notes

[Edge cases, special considerations, why the chosen `timeout_minutes` is right.]
