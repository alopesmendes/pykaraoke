---
description: Guided session for the feature on the current branch, one layer at a time, or the final verify, or ignore to implement it without a walkthrough
argument-hint: "[beginner|intermediate|advanced] or ignore or verify"
model: claude-sonnet-5-5
effort: medium
---

Run the `guide` skill.

- If `$ARGUMENTS` is `verify`, run only its section 5 (Verify) and report each check's real output.
- If `$ARGUMENTS` is `ignore`, run the session in ignore mode: implement the Requirements and edit the
  files, with no walkthrough, then record the header (section 3) and end with verify (section 5).
- Otherwise the level is `$ARGUMENTS`, or `beginner` when it is empty. Any other value: stop and
  list `beginner`, `intermediate`, `advanced` and `ignore`.
- Then start the session: find the feature (section 1), record the level in the checklist header
  (section 3), and show the steps (section 4). Show code only, never edit files.
