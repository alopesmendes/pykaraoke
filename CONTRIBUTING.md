# Contributing

## Setup

```bash
cp .env.example .env
make install        # uv sync — creates .venv and installs everything
make dev            # http://localhost:8000
```

Needs [uv](https://docs.astral.sh/uv/). Full details and troubleshooting land in
`docs/SETUP.md` with Phase 0.2.

## Workflow

1. Pick a checkbox from [docs/EPICS.md](docs/EPICS.md) and open an issue for it.
2. Branch: `feat/<slug>`, `fix/<slug>` or `chore/<slug>`. Never commit to `master`.
3. Write the code, and the test that fails without it.
4. `make check` — lint, tests and audit must be green locally before CI sees them.
5. Update the doc that owns your change (see the table in the `docs-writing` skill) and add a
   `CHANGELOG.md` entry under `## [Unreleased]`.
6. Run `/learning-checklist` — the retention step is part of the feature, not extra.
7. Open the PR and fill the template.

## Branches

`<type>/<issue>-<description>` — the issue number in the branch is what stamps every commit:

```
chore/1-project-setup
feat/12-sign-up-form
fix/23-waiting-list-promotion
```

Types: `feat`, `fix`, `hotfix`, `chore`, `docs`, `style`, `refactor`, `test`, `perf`, `ci`,
`build`, `revert`.

## Commits

Format: `[:gitmoji:] type(#issue): message`

```
:memo: docs(#1): add architecture, security and API documentation
:sparkles: feat(#12): put participants past the seat limit on a waiting list
:bug: fix(#23): promote the oldest waiting participant on cancellation
```

You do not type the `(#issue)` part. `.githooks/prepare-commit-msg` reads it from the branch name
and rewrites the subject:

```bash
git commit -m ":memo: docs: add the security policy"
# stored as: :memo: docs(#1): add the security policy
```

Rules the hook follows:

- The **branch** supplies the issue number and the default type.
- A type you type wins over the branch type — on `chore/1-…`, writing `docs: …` gives
  `docs(#1): …`.
- The gitmoji is optional and kept as-is. See [gitmoji.dev](https://gitmoji.dev).
- It is idempotent, and skips protected branches (`main`, `master`, `develop`, `staging`,
  `release/*`).
- It leaves `fixup!`, `squash!` and `amend!` subjects untouched. `git commit --fixup` reports its
  source as `message`, so without an explicit check the hook would prepend `type(#n):` and
  `git rebase --autosquash` would stop matching the commit.
- It exits during an in-progress rebase, merge, cherry-pick or revert, which replay existing
  subjects rather than writing new ones.
- A branch that does not match `<type>/<number>-…` is left alone entirely.

Install it once per clone:

```bash
ln -sf ../../.githooks/prepare-commit-msg .git/hooks/prepare-commit-msg
```

A symlink, not `core.hooksPath` — `pre-commit install` refuses to run when `core.hooksPath` is
set, and this repo uses both.

Bodies are optional. Add one only when the subject cannot carry the *why*.

## Code style

Ruff is the only formatter and linter — no Black, no Flake8, no isort. `make fmt` fixes what it
can; pre-commit runs it on every commit.

Conventions live in `.claude/skills/`: `python-standards`, `django-mtv`, `clean-architecture`,
`testing`. They are the review checklist too.

## Working with Claude Code

Claude is set up in this repo with 8 skills and 9 agents — see
[docs/AI-WORKFLOW.md](docs/AI-WORKFLOW.md).

**Claude never commits and never pushes.** Both are denied in `.claude/settings.json`. It also
cannot read `.env`. Those rules are enforced by the harness, not by good intentions — leave them
in place.

## Issues

Use the templates: bug, feature, or task. Keep them short — this is a five-person project, not a
change-control board.
