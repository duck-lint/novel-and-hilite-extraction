# Known Failures

Track recurring failure patterns here. This is not a bug dump and not a decision log. A known failure is a pattern later sessions should detect earlier.

## Entry Format

| ID | Pattern | Trigger | Symptom | Likely Cause | Prevention Rule | Cheapest Check | Last Seen | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KF-001 | Active bundle summary drift after seam widening | A detailed seam section is updated after implementation, but later acceptance or runtime-summary sections are not reconciled in the same turn | The active plan or tracker still claims older stage boundaries such as Stage 2-only coverage after Stage 3 already exists | Detailed implementation notes were patched locally while broad summary sections were left stale | After any seam change, re-read and reconcile summary sections in the active plan and tracker before closeout | Grep the active bundle for stale boundary phrases like `Stage 1 and bounded Stage 2 only` or `Stages 3-4 do not exist yet` after a newer seam lands | 2026-05-31 | open |

## Rules

- Add an entry when a failure recurs, spreads, or exposes a harness weakness.
- Keep entries short and searchable.
- Link to evidence in implementation-project files when available.
- Do not record blame, moods, or one-off noise.
- Promote repeatable prevention into tooling or runtime rules when possible.
