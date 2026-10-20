---
name: guide
description: Guided implementation of the feature on the current branch, one layer at a time, with explanations scaled to a level, ending in a verify step. Use when the user types /guide, asks to be walked through an issue's Requirements, asks to implement a feature step by step, or asks to verify a guided session. Also covers /guide ignore, which implements the feature without a walkthrough.
argument-hint: "[beginner|intermediate|advanced] or ignore or verify"
---

# Guide: a guided feature session

By default this skill teaches the feature on the current branch while showing the code. **It
shows code and never edits files**: the user types it themselves, which is the point of a learning
project. The one exception is `ignore` (section 2), where it edits files for every Requirement and
explains nothing. Verify (section 5) is not run in `ignore`: it waits until the user has validated
the Tests checklist.

## 1. Find the feature

1. Issue number: `git branch --show-current`, then the digits after the type prefix
   (`chore/30-guided-feature-...` → `30`). No number: stop and ask which issue.
2. Requirements: `gh issue view N --json body -q .body`. Read only the `## Requirements` section.
3. Tests: `gh pr view --json body`, the Tests checklist of the draft PR. Tests come first.
4. Print the plan: the Requirements numbered, and for each the layers it touches.

If a Requirement is unclear, ask. Do not guess.

## 2. Level

| Source | Result |
|--------|--------|
| the argument is `beginner`, `intermediate` or `advanced` | that level |
| the argument is `ignore` | **ignore mode**: no level, no walkthrough |
| no argument | `beginner`, the first level |
| anything else | stop and list the choices |

The level applies to this session. A new `/guide <level>` call changes it.

**Ignore mode** implements **all** Requirements in the same order as section 4, and edits the files
itself. For each Requirement it writes the tests from the Tests checklist first, then the code, and
runs those tests. It prints a short line per Requirement (done, or what could not be done and why)
and no explanations. It never ticks boxes: that is `issue-orchestrator`. It still records the header
(section 3). It does not run verify (section 5): it stops after the code and says that verify waits
for the validated Tests checklist. The user then runs `/guide verify`.

| Level | How each step is explained |
|-------|----------------------------|
| `beginner` | Line by line, with the reason for each choice. Name each Python or Django concept the first time it appears |
| `intermediate` | One explanation per block. Explain only the non-obvious choices |
| `advanced` | The code and short notes. No walkthrough |

## 3. Record the level in the checklist header

The level lives in the frontmatter of the feature's learning checklist, `docs/learning/NN-<slug>.md`.

- **File missing:** create it with the header below. `NN` is the next free number in the index of
  `docs/learning/README.md`. `/learning-checklist` fills the body at the end.
- **File exists:** update only `level:`.

```yaml
---
name: <slug>
description: <issue title>
branch: <current branch>
issue: <N>
tools: Read, Glob, Grep, Bash, Edit, Write
model: claude-sonnet-5-5
effort: medium
memory: none
level: <beginner|intermediate|advanced>
---
```

## 4. Each step: three parts, in dependency order

Order: **domain, then application, then infrastructure, then interface, then templates.** Inside a
step, the test that proves it comes before the code.

Each step gives:

1. **Layers impacted.** Which of the four layers, and what changes in each. Use the layer table in
   `CLAUDE.md`.
2. **Files.** Create or modify, with paths, function and class names, and the caller of each.
   Names only, no bodies.
3. **Code.** The code, then the explanation for the level above.

Rules that the code must follow:

- Business logic in `services.py` (application), never in a view, serializer, template or model method.
- Interface only parses input, calls one use case, renders the result. No ORM query there.
- User-facing strings through i18n (`gettext` / `gettext_lazy`).
- A layer folder that does not exist yet (`domain/`, `application/`, `infrastructure/`) is created
  as part of the step that first needs it. Say so.

## 5. Verify (ends every walkthrough session)

Run `/guide verify`. Run each check, and print its real output. Do not summarise a failure.
`/guide ignore` never runs this section; its verify is the separate `/guide verify` call, made
after the Tests checklist is validated.

| # | Check | Command |
|---|-------|---------|
| 1 | Lint | `make lint` |
| 2 | Tests | `make test` |
| 3 | Django checks | `uv run python manage.py check` |
| 4 | Layer imports | the grep rules below |
| 5 | Docs, changelog, checklist | the git and file checks below |

For each problem, print three lines: **Wrong:** what failed. **Why it matters:** the consequence.
**Fix:** the change to make. Do not apply the fix; the user does.

For a large batch, also run the `verifier` agent for the convention review.

### Layer imports

| Layer | Must not import |
|-------|-----------------|
| `domain/` | `django`, `rest_framework`, `application`, `infrastructure`, `interface` |
| `application/` | `django`, `rest_framework`, `infrastructure`, `interface` |
| `infrastructure/` | `interface` |
| `interface/` | `infrastructure` |

A layer folder that does not exist is reported as `not present yet, skipped`. It is not a failure.

```bash
# A missing folder prints nothing (2>/dev/null): report it as "not present yet, skipped".
grep -rnE "^\s*(from|import) (django|rest_framework|application|infrastructure|interface)\b" domain/ 2>/dev/null
grep -rnE "^\s*(from|import) (django|rest_framework|infrastructure|interface)\b" application/ 2>/dev/null
grep -rnE "^\s*(from|import) interface\b" infrastructure/ 2>/dev/null
grep -rnE "^\s*(from|import) infrastructure\b" interface/ 2>/dev/null
```

Any match is a problem. Report the file and line.

### Docs, changelog, checklist

| Check | Passes when |
|-------|-------------|
| Owning doc | a file under `docs/` changed, for each behaviour change. The owner is in the `docs-writing` skill table |
| Changelog | `CHANGELOG.md` changed, with an entry under `## [Unreleased]` |
| Learning checklist | `docs/learning/NN-<slug>.md` exists, its header has `level:`, and the index in `docs/learning/README.md` lists it |

Check with `git diff master --name-only`, `git status --short` (new files are untracked until
committed, so `diff` alone misses them) and `ls docs/learning/`. A missing item is a problem. The
fix is to edit the doc or run `/learning-checklist`.

## Stop, do not skip

- A Requirement is unclear: ask.
- A check cannot run: report it as `could not run`, with the reason. Never as passed.
- A step needs a decision the issue does not make: ask.

## See also

- Layer table and rules: `CLAUDE.md` (Architecture)
- Checklist template: `docs/learning/TEMPLATE.md`
- Owner of each doc: skill `docs-writing`
