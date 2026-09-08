---
name: learning-checklist
description: Create or update the learning checklist in docs/learning/ for the feature just worked on, so the user retains the Python/Django concepts instead of only shipping code. Use at the end of every feature or milestone chunk, or when the user asks what they should learn, revise, or be quizzed on.
argument-hint: "[feature name, e.g. sign-up-form]"
---

# Learning checklist

This project exists to **learn Django and Python**, not only to ship a karaoke site. Shipped code
with nothing retained is a failed feature.

Produce or update one file per feature in `docs/learning/`, following `docs/learning/TEMPLATE.md`.

## Steps

1. **Name the file.** `docs/learning/NN-<feature-slug>.md`, `NN` being the next free two-digit
   number. If a file for this feature exists, **update it** — never create a duplicate.
2. **Look at what actually happened**, not at what was planned:
   - `git diff` / `git log` for this feature's changes
   - the files created or modified in this session
   - any error, failed test, or wrong turn hit along the way — those are the best entries
3. **Fill each section** of the template:
   - **Concepts** — the 3–6 ideas the code depends on. Name them precisely (`select_related` vs
     `prefetch_related`, not "the ORM").
   - **Docs to read** — real links, Django docs first, deep-linked to the section.
   - **Hands-on** — checkboxes the user can do *without* Claude, in this repo.
   - **Quiz** — 4–6 questions answerable from memory, no lookup. Include the answer in a
     `<details>` block so it is hidden until wanted.
   - **Gotchas** — what actually went wrong this session, and the fix.
4. **Link it** from `docs/learning/README.md`'s index table.
5. **Report** the path and the concept list in your reply.

## Rules

- **Specific to this repo.** "Learn about forms" is useless. "Why `clean_pseudo` strips whitespace
  before validating length, and what happens if it does not" is useful.
- **Honest about gaps.** If a concept was used but glossed over — a decorator, a context manager,
  a metaclass — say so and put it in the checklist. Do not hide the parts that were handed over.
- **Quiz questions must have one correct answer** and be answerable from the checklist itself.
- **Never mark a checkbox for the user.** They tick their own boxes.
- Keep the whole file under 100 lines. A checklist nobody finishes teaches nothing.

## Example entry

```markdown
### Concepts

- **`select_related` vs `prefetch_related`** — one SQL JOIN vs a second query plus a Python-side
  join. Forward FK uses the first; reverse FK and M2M need the second.
- **`transaction.atomic()`** — why `reserve_seat` wraps two writes: without it, a crash between
  them leaves a participant with no confirmation email and no way to detect it.

### Quiz

1. `Participant.objects.select_related("event")` — how many queries for 20 participants?
   <details><summary>Answer</summary>One. The FK is JOINed into the same query.</details>
```

## See also

- Template: `docs/learning/TEMPLATE.md`
- Index: `docs/learning/README.md`
- Where this step sits in the loop: `docs/AI-WORKFLOW.md`
