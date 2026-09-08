# pykaraoke

*A small private site where friends sign up for karaoke night and pick their songs in advance.*

One unguessable link per event. No accounts, no passwords, no app to install. Open the link, put
your pseudo in, choose your songs, see who else is coming.

It is also a **learning project** — every feature ships with a checklist in
[`docs/learning/`](docs/learning/) of what the code actually taught.

## Status

🚧 **Milestone 0 — foundation.** No feature code yet. See [docs/EPICS.md](docs/EPICS.md).

| Milestone | Scope                              | State       |
|-----------|------------------------------------|-------------|
| 0         | Docs, CI/CD, AI workflow           | in progress |
| 1         | App skeleton, settings split, i18n | todo        |
| 2         | Link access + sign-up form         | todo        |
| 3         | Overviews, song requests, admin    | todo        |

## Quickstart

*Available once Phase 0.2 lands.*

```bash
git clone https://github.com/alopesmendes/pykaraoke.git
cd pykaraoke
cp .env.example .env
make install
make dev            # http://localhost:8000
```

Postgres and a local mail catcher are optional: `make db-up`. Without them the app runs on SQLite
and prints emails to the console.

## Stack

Django 6.1 · Python 3.13+ · PostgreSQL 17 · uv · Ruff · pytest-django

Server-rendered MTV. No SPA, no REST API, no JavaScript build step — the toaster and the
confirmation modal are progressive enhancement over working HTML forms.

## Documentation

| File                                 | Answers                                 |
|--------------------------------------|-----------------------------------------|
| [ARCHITECTURE](docs/ARCHITECTURE.md) | How it is structured, and why           |
| [DATABASE](docs/DATABASE.md)         | Models, constraints, data retention     |
| [API](docs/API.md)                   | Routes, forms, responses                |
| [SECURITY](docs/SECURITY.md)         | Link access, personal data, secrets     |
| [AI-WORKFLOW](docs/AI-WORKFLOW.md)   | How Claude Code is wired into this repo |
| [EPICS](docs/EPICS.md)               | Roadmap as checkboxes                   |
| [learning/](docs/learning/)          | What to learn from each feature         |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: branch, `make check`, open a PR.

## License

MIT — see [LICENSE](LICENSE).
