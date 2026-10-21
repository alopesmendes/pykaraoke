# Epics

*The roadmap as checkable work. One epic per milestone.*

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

---

## Milestone 0: Foundation & infrastructure

**Goal:** the repo can be worked in. Documented, linted, tested, and wired to an AI workflow.
**Done when:** `make check` is green and a new feature can start without touching infrastructure.

### 0.1 Documentation & templates
- [x] `docs/ARCHITECTURE.md`. MTV flow, layout, service layer
- [x] `docs/DATABASE.md`. ER diagram, models, retention
- [x] `docs/API.md`. Routes, forms, responses
- [x] `docs/SECURITY.md`. Access, PII, purge, secrets
- [x] `docs/EPICS.md`. This file
- [x] `docs/learning/`. Template, index, milestone 0 checklist
- [x] `.github/ISSUE_TEMPLATE/` + `pull_request_template.md`
- [x] `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

### 0.3 AI workflow
- [x] `.claude/settings.json`. Permissions and format hook
- [x] 7 skills under `.claude/skills/`
- [x] 8 agents under `.claude/agents/`
- [x] 3 commands under `.claude/commands/`
- [x] `CLAUDE.md`. The index
- [x] `docs/AI-WORKFLOW.md`. The guideline

### 0.2 CI/CD & tooling *(built in learning mode: quiz before each chunk)*
- [x] `pyproject.toml` + `uv.lock`
- [x] `settings.py` env wiring + `.env.example`
- [x] `tests/` smoke test + pytest config
- [x] `Makefile`, `.pre-commit-config.yaml`, `.gitignore`
- [x] `Dockerfile`, `docker-compose.yml`
- [x] CI workflow (`ci.yml`, one pipeline)
- [x] `deploy-dev.yml`, `deploy-prod.yml`
- [x] `docs/SETUP.md`, `docs/CI-CD.md`

**Milestone 0 complete.** `make check` is green; every workflow validates with `actionlint`; the
full gotcha list is in `docs/learning/00-milestone-0-foundation.md`.

---

## Milestone 1: Project architecture

**Goal:** the `karaoke` app exists with its layers in place and nothing in it yet.
**Done when:** an empty app boots, settings are split per environment, and the test tooling proves it.

- [x] `python manage.py startapp karaoke` (#3)
- [x] Settings split: `settings/base.py`, `dev.py`, `prod.py` (#4)
- [x] Wire PostgreSQL via `DATABASE_URL` (#5)
- [x] Create the layer files: `services.py`, `exceptions.py`, `managers.py` (#6)
- [x] `templates/base.html` with content block, toaster region, modal container (#7)
- [x] i18n setup: `LANGUAGE_CODE = "fr"`, `LANGUAGES = [fr, ja]`, `locale/` directory (#8)
- [x] Static files pipeline (WhiteNoise) (#9)
- [x] `tests/factories.py` scaffold + `conftest.py` fixtures (#10)
- [x] Deploy backend to Render, dev and prod, tag-driven CI/CD and Swagger (#26)
- [x] Spec-driven GitHub setup: issue and PR templates, labels (#22)
- [x] Claude setup trimmed to what the project uses (#29)
- [x] `/guide` guided feature skill with a final verify (#30)
- [x] CI split into BUILD, LINT, TEST, ANALYSIS/SECURITY, DEPLOY (#31)
- [ ] Learning checklist for the milestone

---

## Milestone 2: Access & sign-up

**Goal:** a friend with the link can sign up and gets a confirmation.
**Done when:** the sign-up form writes a `Participant` and the waiting list behaves.

- [ ] Models: `KaraokeEvent`, `AccessLink`, `Participant` + constraints + migration
- [ ] `AccessLink` token generation and constant-time lookup
- [ ] Token middleware/decorator. 404 on unknown or expired
- [ ] Rate limiting on write routes
- [ ] `SignUpForm` with every validation rule from `docs/API.md`
- [ ] `services.reserve_seat()`. Confirm or waitlist, atomic
- [ ] `karaoke:enter` and `karaoke:sign_up` views + templates
- [ ] Toaster on success / waiting list
- [ ] Confirmation email or SMS
- [ ] Tests: models, form, service, views, N+1
- [ ] `security-reviewer` pass before merge
- [ ] Learning checklist for the milestone

---

## Milestone 3: Overviews & songs

**Goal:** everyone sees who is coming; the admin can manage the night.
**Done when:** both overview pages render in O(1) queries and cancellation promotes the waiting list.

- [ ] `SongRequest` model + migration
- [ ] `karaoke:overview`. Participants, statuses, own row highlighted
- [ ] `karaoke:update_status` and `karaoke:cancel` + confirmation modal
- [ ] `services.cancel_participation()`. Promotes the oldest waiting participant, atomic
- [ ] `karaoke:songs`. Song request formset, `MAX_SONGS_PER_PARTICIPANT`
- [ ] `karaoke:admin_overview`. Staff-only, cancel anyone
- [ ] `purge_expired_data` management command + scheduled run
- [ ] `django_assert_num_queries` tests on both overviews
- [ ] Accessibility pass on modal and toaster
- [ ] Learning checklist for the milestone

---

## Working rules

- One issue per checkbox, one PR per issue, `feat/`, `fix/` or `chore/` branch.
- Every feature ends with a learning checklist. Run `/learning-checklist`.
- Every change to behaviour updates the doc that owns it (see the `docs-writing` skill).
- `/commit-push-pr` commits and pushes; `issue-orchestrator` opens the draft PR and marks it ready.
  Claude never merges. Merging is the human's move.

## See also

- The loop each feature runs through: [AI-WORKFLOW.md](AI-WORKFLOW.md)
- What already exists: [ARCHITECTURE.md](ARCHITECTURE.md)
