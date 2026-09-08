# pykaraoke

Private Django site where a group of friends sign up for karaoke nights and pick their songs.
A learning project: **understanding the code matters as much as shipping it.**

## Stack

Django 6.1 · Python 3.13+ · PostgreSQL 17 (SQLite locally is fine) · uv · Ruff · pytest-django ·
server-rendered MTV, no SPA, no REST API.

## Hard rules

1. **Never `git commit` or `git push`.** Denied in `.claude/settings.json`. The human commits.
2. **Never read `.env`.** Denied. Use `.env.example` to learn the keys.
3. **Business logic goes in `services.py`**, never in a view or a template.
4. **Every behaviour change updates the doc that owns it** — see the table in the `docs-writing`
   skill — and `CHANGELOG.md` under `## [Unreleased]`.
5. **Every feature ends with `/learning-checklist`.** Shipped-but-not-understood is not done.
6. **Skills stay under 200 lines.** Register new ones here and in `docs/AI-WORKFLOW.md`.
7. English for code, docs and commits. French (then Japanese) for user-facing strings, via i18n.

## Commands

*Phase 0.2 builds these — until then, none of them exist yet.*

```bash
make install     # uv sync
make dev         # runserver
make test        # pytest
make lint        # ruff check + ruff format --check
make audit       # bandit + pip-audit + manage.py check --deploy
make check       # the full local gate — run before every PR
make db-up       # docker compose: postgres + mailpit
```

## Where to look

| Need                                  | Use                                            |
|---------------------------------------|------------------------------------------------|
| Models, ORM, migrations, N+1          | skill `django-mtv` → agent `backend-patterns`  |
| Views, forms, URL design              | skill `django-mtv` → agent `api-designer`      |
| Templates, toaster, modal, i18n, a11y | agent `frontend-patterns`                      |
| Where should this code live?          | skill `clean-architecture`                     |
| Python style, type hints, exceptions  | skill `python-standards`                       |
| Writing tests                         | skill `testing` → agent `eval-harness`         |
| Did it actually pass?                 | agent `verifier`                               |
| Convention review before a PR         | agent `coding-standards`                       |
| Auth, tokens, personal data           | agent `security-reviewer` + `docs/SECURITY.md` |
| CI, workflows, secrets                | skill `github-actions`                         |
| Docker, env vars, deploy              | skill `devops`                                 |
| Writing or updating docs              | skill `docs-writing` → agent `doc-writer`      |
| "Does this API really work that way?" | agent `doc-lookup`                             |
| Finished a feature                    | `/learning-checklist`                          |

## Docs

| File                                         | Answers                                  |
|----------------------------------------------|------------------------------------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How is it structured, and why            |
| [docs/DATABASE.md](docs/DATABASE.md)         | Models, constraints, retention           |
| [docs/API.md](docs/API.md)                   | Routes, forms, responses, toaster levels |
| [docs/SECURITY.md](docs/SECURITY.md)         | Access, PII, purge, secrets              |
| [docs/AI-WORKFLOW.md](docs/AI-WORKFLOW.md)   | How to work with Claude here             |
| [docs/EPICS.md](docs/EPICS.md)               | What is built, what is next              |
| [docs/learning/](docs/learning/)             | What to learn from each feature          |

`docs/SETUP.md` and `docs/CI-CD.md` arrive with Phase 0.2.

## Layout

```
pykaraoke/   project config only        karaoke/   the single app (Milestone 1+)
tests/       mirrors the source tree    docs/      the files above
.claude/     8 skills, 9 agents, permissions, format hook
```

## Status

Milestone 0 — Phases 0.1 and 0.3 done, Phase 0.2 in progress. See `docs/EPICS.md`.
