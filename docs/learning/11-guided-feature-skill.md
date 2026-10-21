# 11: Guided feature skill with levels and a final verify

*What to learn from building `/guide`. Milestone 1.*

**Shipped:** `/guide [level]` shows a feature's steps by layer, and `/guide verify` runs the checks.
**Files:** `.claude/skills/guide/SKILL.md`, `.claude/commands/guide.md`, `CLAUDE.md`, `docs/AI-WORKFLOW.md`

---

## Concepts

- **Dependency rule**: `domain/` imports nothing outside the standard library, `application/`
  imports only `domain/`. Without it, a Django model change silently changes a business rule.
  The guide's verify step checks it with grep, because no test enforces it yet.
- **Anchored regex for import checks**: `^\s*(from|import) django\b` matches only real import lines.
  Without `^`, a docstring that mentions "django" fails the check. Without `\b`, `djangonaut` matches.
- **YAML frontmatter as a config header**: `key: value` lines between `---` markers. Agents and
  skills use it, and so does the checklist's `level:`. No code parses it yet, so a typo in the
  key is silent.
- **Make stops at the first failing target**: `make check` runs `lint test audit collectstatic`
  in order. A failing `audit` hides whether `collectstatic` would pass.

## Docs to read

- [ ] [Regular expression HOWTO](https://docs.python.org/3/howto/regex.html). Anchors and `\b`.
- [ ] [Translation, `gettext_lazy`](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/).
      Why the guide asks for i18n on every user-facing string.

## Hands-on

Do these in this repo, without Claude.

- [ ] Run `/guide intermediate` on a branch with a linked issue. Then run `/guide` with no argument
      and open the checklist header: `level` must read `beginner`.
- [ ] Put `from django.db import models` in a scratch `domain/entities.py`, run the grep from the
      verify section, and read the match. Delete the file afterwards.
- [ ] Run `make check` and read the `audit` output. Find the advisory and say why it does not
      touch this feature.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. Why does the import grep start with `^\s*`?
   <details><summary>Answer</summary>So it matches only lines that begin with an import, not a string or comment that mentions the package.</details>
2. A `/guide` call has no argument, and the checklist header says `level: intermediate`. Which level runs?
   <details><summary>Answer</summary>`beginner`. With no argument the first level always applies. The header is written, not read.</details>
3. Can `application/` import `infrastructure/`?
   <details><summary>Answer</summary>No. Application depends on interfaces it declares. Infrastructure implements them and is wired in at the edge.</details>
4. Why does `make check` show the `audit` error even when the tests pass?
   <details><summary>Answer</summary>`audit` is a separate target. Its failure stops `make check` after lint and tests, so `collectstatic` does not run.</details>

## Gotchas hit

- **Duplicate `### Added` heading** → added the entry under a new heading → merged it into the
  existing `### Added` list.
- **Dead loop in a grep check** → a `for` loop that only echoed did nothing → removed it, and
  kept the missing-folder note in text.
- **Layer folders absent** → the verify grep reports nothing for `domain/`, and that looks like
  a pass → the verify output now says `not present yet, skipped` by rule.
- **Baseline already red** → `make check` fails on `pip-audit` (certifi advisory) before any change
  of this feature → reported, not fixed here.

## Still unclear

- Whether the level should be read from the header when no argument is given. The spec says
  always `beginner`, so the header is a record only.
- The `tools`, `model`, `effort`, `memory` fields in the header have no reader yet.
