# Epics

*The roadmap as checkable work. One epic per milestone.*

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

---

## Milestone 0 — Foundation & infrastructure

**Goal:** the repo can be worked in — documented, linted, tested, and wired to an AI workflow.
**Done when:** `make check` is green and a new feature can start without touching infrastructure.

### 0.1 Documentation & templates
- [x] `docs/ARCHITECTURE.md` — MTV flow, layout, service layer
- [x] `docs/DATABASE.md` — ER diagram, models, retention
- [x] `docs/API.md` — routes, forms, responses
- [x] `docs/SECURITY.md` — access, PII, purge, secrets
- [x] `docs/EPICS.md` — this file
- [x] `docs/learning/` — template, index, milestone 0 checklist
- [x] `.github/ISSUE_TEMPLATE/` + `pull_request_template.md`
- [x] `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

### 0.3 AI workflow
- [x] `.claude/settings.json` — permissions and format hook
- [x] 8 skills under `.claude/skills/`
- [x] 9 agents under `.claude/agents/`
- [x] `CLAUDE.md` — the index
- [x] `docs/AI-WORKFLOW.md` — the guideline

### 0.2 CI/CD & tooling *(built in learning mode — quiz before each chunk)*
- [ ] `pyproject.toml` + `uv.lock`
- [ ] `settings.py` env wiring + `.env.example`
- [ ] `tests/` smoke test + pytest config
- [ ] `Makefile`, `.pre-commit-config.yaml`, `.gitignore`
- [ ] `Dockerfile`, `docker-compose.yml`
- [ ] `lint.yml`, `test.yml`
- [ ] `security.yml`, `deploy.yml`
- [ ] `docs/SETUP.md`, `docs/CI-CD.md`

---

## Milestone 1 — Project architecture

**Goal:** the `karaoke` app exists with its layers in place and nothing in it yet.
**Done when:** an empty app boots, settings are split per environment, and the test tooling proves it.

- [ ] `python manage.py startapp karaoke`
- [ ] Settings split: `settings/base.py`, `dev.py`, `prod.py`
- [ ] Wire PostgreSQL via `DATABASE_URL`
- [ ] Create the layer files: `services.py`, `exceptions.py`, `managers.py`
- [ ] `templates/base.html` with content block, toaster region, modal container
- [ ] i18n setup: `LANGUAGE_CODE = "fr"`, `LANGUAGES = [fr, ja]`, `locale/` directory
- [ ] Static files pipeline (WhiteNoise)
- [ ] `tests/factories.py` scaffold + `conftest.py` fixtures
- [ ] Learning checklist for the milestone

---

## Milestone 2 — Access & sign-up

**Goal:** a friend with the link can sign up and gets a confirmation.
**Done when:** the sign-up form writes a `Participant` and the waiting list behaves.

- [ ] Models: `KaraokeEvent`, `AccessLink`, `Participant` + constraints + migration
- [ ] `AccessLink` token generation and constant-time lookup
- [ ] Token middleware/decorator — 404 on unknown or expired
- [ ] Rate limiting on write routes
- [ ] `SignUpForm` with every validation rule from `docs/API.md`
- [ ] `services.reserve_seat()` — confirm or waitlist, atomic
- [ ] `karaoke:enter` and `karaoke:sign_up` views + templates
- [ ] Toaster on success / waiting list
- [ ] Confirmation email or SMS
- [ ] Tests: models, form, service, views, N+1
- [ ] `security-reviewer` pass before merge
- [ ] Learning checklist for the milestone

---

## Milestone 3 — Overviews & songs

**Goal:** everyone sees who is coming; the admin can manage the night.
**Done when:** both overview pages render in O(1) queries and cancellation promotes the waiting list.

- [ ] `SongRequest` model + migration
- [ ] `karaoke:overview` — participants, statuses, own row highlighted
- [ ] `karaoke:update_status` and `karaoke:cancel` + confirmation modal
- [ ] `services.cancel_participation()` — promotes the oldest waiting participant, atomic
- [ ] `karaoke:songs` — song request formset, `MAX_SONGS_PER_PARTICIPANT`
- [ ] `karaoke:admin_overview` — staff-only, cancel anyone
- [ ] `purge_expired_data` management command + scheduled run
- [ ] `django_assert_num_queries` tests on both overviews
- [ ] Pick the deploy provider and fill the `deploy.yml` TODO steps
- [ ] Accessibility pass on modal and toaster
- [ ] Learning checklist for the milestone

---

## Working rules

- One issue per checkbox, one PR per issue, `feat/`, `fix/` or `chore/` branch.
- Every feature ends with a learning checklist — run `/learning-checklist`.
- Every change to behaviour updates the doc that owns it (see the `docs-writing` skill).
- Claude never commits or pushes. That is the human's move.

## See also

- The loop each feature runs through: [AI-WORKFLOW.md](AI-WORKFLOW.md)
- What already exists: [ARCHITECTURE.md](ARCHITECTURE.md)
