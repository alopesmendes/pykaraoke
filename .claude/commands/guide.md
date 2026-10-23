---
description: Guided session for the feature on the current branch, one layer at a time, or the final verify, or next to verify, commit and show the next step, or ignore to implement it without a walkthrough
argument-hint: "[beginner|intermediate|advanced] or ignore or verify or next"
model: claude-sonnet-5-5
effort: medium
---

Run the `guide` skill.

- If `$ARGUMENTS` is `verify`, run only its section 5 (Verify) and report each check's real output.
- If `$ARGUMENTS` is `ignore`, run the session in ignore mode: implement the Requirements and edit the
  files, with no walkthrough, then record the header (section 3) and end with verify (section 5).
- If `$ARGUMENTS` is `next`, close the current step and open the following one:
  1. Run verify (section 5) and print each check's real output.
  2. Any check fails: stop. No commit, no next step. Print Wrong, Why it matters, Fix, and wait.
  3. All pass: commit only the files of the step just finished, by name. Never `git add -A` or `.`,
     and leave unrelated modified files alone (list them). Message `feat(#N): <what the step
     added>`, English, with the commit attribution lines. Do not push, do not tick boxes.
  4. Show the next step (section 4) at the level in the checklist header (`level:`), or `beginner`
     when the header has none. All steps done: say so and point to `/learning-checklist`.
  5. Docs, changelog and learning checklist (section 5, last table) are reported but do not block a
     step commit. They must pass before `/commit-push-pr`.
- Otherwise the level is `$ARGUMENTS`, or `beginner` when it is empty. Any other value: stop and
  list `beginner`, `intermediate`, `advanced`, `ignore`, `verify` and `next`.
- Then start the session: find the feature (section 1), record the level in the checklist header
  (section 3), and show the steps (section 4). Show code only, never edit files. The only commands
  that write to git are `next` (commit) and, when asked, a fix the user requested.
