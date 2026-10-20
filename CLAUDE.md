# pykaraoke

Private Django site where a group of friends sign up for karaoke nights and pick their songs.
A learning project: **understanding the code matters as much as shipping it.**

## Stack

Django 6.1 · Python 3.13+ · PostgreSQL 17 (SQLite locally is fine) · uv · Ruff · pytest-django ·
Django REST Framework for the interface layer. Clean architecture, see [Architecture](#architecture).

## Hard rules

Permissions (git, `gh`, `.env`) live in `.claude/settings.json`; these rules cover the rest.

1. **Config keys come from `.env.example`.** It is the only env file to learn from.
2. **Business logic goes in the domain or in `application/<context>/services.py`**, never in a
   view, a serializer, a template or an ORM model. See [Architecture](#architecture).
3. **Every behaviour change updates the doc that owns it**: see the table in the `docs-writing`
   skill. And `CHANGELOG.md` under `## [Unreleased]`.
4. **Every feature ends with `/learning-checklist`.** Shipped-but-not-understood is not done.
5. **Skills stay under 200 lines.** Register new ones here and in `docs/AI-WORKFLOW.md`.
6. English for code, docs and commits. French (then Japanese) for user-facing strings, via i18n.
7. **Issue and PR state belongs to `issue-orchestrator`.** Labels, draft and ready, and ticked
   boxes change only through it. No code before the Tests checklist is validated, and no code
   before the draft PR exists.

## Working principles

1. **Don't assume.** If a specification is missing, ask for it. Surface trade-offs before
   choosing between approaches, instead of picking silently.
2. **Minimum code, nothing speculative.** Solve the problem in front of you. Don't build a whole
   architecture for a small problem: no bazooka for a fist fight.
3. **Touch only what you must.** Every changed line should trace back to the request. Leave
   unrelated code, comments and formatting alone.
4. **Define success criteria.** State how the work is verified before starting. Loop until the
   criteria pass, while still respecting the other principles on every iteration.

## Architecture

Clean architecture in four layers. Dependencies point inward: interface → application → domain.
Infrastructure implements the interfaces that application declares.

| Layer          | Path                                             | May import                                    | Holds                                                |
|----------------|--------------------------------------------------|-----------------------------------------------|------------------------------------------------------|
| Domain         | `domain/<context>/`                              | Python standard library only                  | entities, value objects, business rules, exceptions  |
| Application    | `application/<context>/`                         | domain                                        | use cases in `services.py`, ports in `interfaces.py` |
| Infrastructure | `infrastructure/db/`, `infrastructure/external/` | domain, application, Django, third-party SDKs | Django models, repositories, gateway clients         |
| Interface      | `interface/api/<context>/`                       | application, Django, DRF                      | serializers, views, urls                             |

1. **Domain imports no Django and no DRF.** Entities are plain Python. The ORM never leaks into them.
2. **Application depends on interfaces, not implementations.** Use cases receive repositories and
   gateways as arguments, typed against `interfaces.py`. They never import from `infrastructure/`.
3. **Infrastructure maps, it does not decide.** Repositories translate between Django models
   (`infrastructure/db/<context>/models.py`) and domain entities.
4. **Interface translates, it does not decide.** A view parses input with a serializer, calls one
   use case, and renders the result. No business rule and no direct ORM query.
5. **The frontend decides no business rules.** A client may check input for UX, but the rule is
   enforced in domain or application, and the API returns the outcome.
6. **Tests mirror the layers.** `tests/domain/` and `tests/application/` run without a database.
   Import boundaries are checked in review until an automated check exists.

## Commands

```bash
make install     # uv sync
make dev         # runserver
make test        # pytest
make lint        # ruff check + ruff format --check
make audit       # bandit + pip-audit + manage.py check --deploy
make check       # the full local gate, run before every PR
make db-up       # docker compose: postgres + mailpit
```

## Where to look

| Need                                      | Use                                                  |
|-------------------------------------------|------------------------------------------------------|
| Models, ORM, migrations, N+1              | skill `django-mtv` → agent `backend-patterns`        |
| Views, forms, URL design                  | skill `django-mtv` → agent `api-designer`            |
| Where should this code live?              | skill `django-mtv` (`layers-and-python.md`)          |
| Python style, type hints, exceptions      | skill `django-mtv` (`layers-and-python.md`)          |
| Writing tests                             | skill `testing` → agent `eval-harness`               |
| Did it actually pass?                     | agent `verifier`                                     |
| Convention review before a PR             | agent `verifier`                                     |
| Auth, tokens, personal data               | agent `security-reviewer` + `docs/SECURITY.md`       |
| CI, workflows, secrets                    | skill `github-actions`                               |
| Docker, env vars, deploy                  | skill `devops`                                       |
| Writing or updating docs                  | skill `docs-writing` → agent `doc-writer`            |
| Phrasing an explanation, PR text, comment | skill `docs-writing`                                 |
| "Does this API really work that way?"     | agent `doc-lookup`                                   |
| Launch an issue's Requirements            | `/karaoke-issue-launch` → agent `issue-orchestrator` |
| Guided walkthrough of a feature, by level | `/guide [level]` → skill `guide`                     |
| Verify a guided session                   | `/guide verify` → skill `guide`                      |
| Issue state, draft PR, labels, ready      | agent `issue-orchestrator`                           |
| Finished a feature                        | `/learning-checklist`                                |

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
| [docs/SETUP.md](docs/SETUP.md)               | Fresh clone to a running dev server      |
| [docs/CI-CD.md](docs/CI-CD.md)               | What each workflow does, what's missing  |

## Layout

Target layout, built from Milestone 1 on. One folder per `<context>` in every layer.

```
pykaraoke/
    config/                  # Django settings, urls, wsgi/asgi
    domain/                  # Business rules, no framework imports
        <context>/
            entities.py
            exceptions.py
    application/             # Use cases
        <context>/
            services.py
            interfaces.py    # Abstract repositories and gateways
    infrastructure/          # Implementations
        db/
            <context>/
                models.py
                repositories.py
        external/            # Third-party gateways
    interface/               # Django REST Framework
        api/
            <context>/
                serializers.py
                views.py
                urls.py
    tests/                   # mirrors the layers above
    docs/                    # the files in Docs
    manage.py
.claude/     7 skills, 8 agents, 3 commands, permissions, format hook
```
